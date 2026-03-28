/*
 * Flash-Wear-Aware Persistent Data Logger
 *
 * Stores periodic sensor readings to NVS. Designed for years of operation:
 *   - Uses NVS wear leveling (not raw flash_write)
 *   - Writes every 10 seconds (not every tick) to limit flash wear
 *   - Static buffers only — no heap allocation in the main loop
 *   - Handles NVS full (ENOSPC) gracefully
 *   - Persists sample counter as uint32_t (wraps cleanly at 4B samples)
 */

#include <zephyr/kernel.h>
#include <zephyr/fs/nvs.h>
#include <zephyr/storage/flash_map.h>

/* NVS keys */
#define NVS_ID_SAMPLE_COUNT  1U
#define NVS_ID_LAST_VALUE    2U

/* Write interval: 10 s — limits flash write cycles for long-term operation */
#define WRITE_INTERVAL  K_SECONDS(10)

/* NVS partition — uses storage_partition defined in the board DTS */
#define NVS_PARTITION        FIXED_PARTITION_ID(storage_partition)
#define NVS_PARTITION_DEVICE FIXED_PARTITION_DEVICE(storage_partition)
#define NVS_PARTITION_OFFSET FIXED_PARTITION_OFFSET(storage_partition)

static struct nvs_fs fs;

static int nvs_init_storage(void)
{
    int ret;
    struct flash_pages_info info;
    const struct device *flash_dev = NVS_PARTITION_DEVICE;

    if (!device_is_ready(flash_dev)) {
        printk("Flash device not ready\n");
        return -ENODEV;
    }

    fs.flash_device = flash_dev;
    fs.offset = NVS_PARTITION_OFFSET;

    ret = flash_get_page_info_by_offs(flash_dev, fs.offset, &info);
    if (ret < 0) {
        printk("flash_get_page_info failed: %d\n", ret);
        return ret;
    }

    fs.sector_size = (uint16_t)info.size;
    fs.sector_count = 4U;  /* 4 sectors provides adequate wear leveling */

    ret = nvs_mount(&fs);
    if (ret < 0) {
        printk("nvs_mount failed: %d\n", ret);
        return ret;
    }

    return 0;
}

/* Read the persisted sample counter; return 0 on first boot. */
static uint32_t read_sample_count(void)
{
    uint32_t count = 0U;
    ssize_t rc = nvs_read(&fs, NVS_ID_SAMPLE_COUNT, &count, sizeof(count));

    if (rc < 0) {
        /* -ENOENT on first boot — treat as zero */
        count = 0U;
    }
    return count;
}

/* Persist both counter and latest sensor value. */
static int write_sample(uint32_t count, uint32_t value)
{
    int ret;

    ret = nvs_write(&fs, NVS_ID_SAMPLE_COUNT, &count, sizeof(count));
    if (ret < 0) {
        if (ret == -ENOSPC) {
            printk("NVS full — storage exhausted, continuing without write\n");
        } else {
            printk("nvs_write count failed: %d\n", ret);
        }
        return ret;
    }

    ret = nvs_write(&fs, NVS_ID_LAST_VALUE, &value, sizeof(value));
    if (ret < 0) {
        if (ret == -ENOSPC) {
            printk("NVS full — storage exhausted, continuing without write\n");
        } else {
            printk("nvs_write value failed: %d\n", ret);
        }
        return ret;
    }

    return 0;
}

/* Simulate a sensor: deterministic counter-based value. */
static uint32_t read_sensor(uint32_t tick)
{
    return (tick * 31U + 7U) & 0xFFFFU;
}

int main(void)
{
    int ret;
    uint32_t sample_count;
    uint32_t sensor_value;

    ret = nvs_init_storage();
    if (ret < 0) {
        printk("Storage init failed: %d\n", ret);
        return ret;
    }

    sample_count = read_sample_count();
    printk("Boot: resuming from sample count %u\n", sample_count);

    while (true) {
        sensor_value = read_sensor(sample_count);
        sample_count++;

        ret = write_sample(sample_count, sensor_value);
        if (ret < 0 && ret != -ENOSPC) {
            printk("Write error %d — continuing\n", ret);
        }

        printk("sample=%u value=%u\n", sample_count, sensor_value);

        k_sleep(WRITE_INTERVAL);
    }

    return 0;
}
