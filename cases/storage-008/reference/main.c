#include <zephyr/kernel.h>
#include <zephyr/fs/nvs.h>
#include <zephyr/storage/flash_map.h>
#include <string.h>

#define NVS_PARTITION        storage_partition
#define NVS_PARTITION_DEVICE FIXED_PARTITION_DEVICE(NVS_PARTITION)
#define NVS_PARTITION_OFFSET FIXED_PARTITION_OFFSET(NVS_PARTITION)

#define CONFIG_ID_PRIMARY 1U
#define CONFIG_ID_TEMP    2U

struct app_config {
	uint32_t version;
	uint32_t value;
};

static struct nvs_fs nvs = {
	.flash_device = NVS_PARTITION_DEVICE,
	.offset = NVS_PARTITION_OFFSET,
	.sector_size = 4096,
	.sector_count = 2,
};

static int atomic_config_update(struct app_config *new_cfg)
{
	struct app_config verify_buf;
	ssize_t ret;

	/* Step 1: Write new config to temp slot */
	ret = nvs_write(&nvs, CONFIG_ID_TEMP, new_cfg, sizeof(*new_cfg));
	if (ret < 0) {
		printk("nvs_write temp failed: %d\n", (int)ret);
		return (int)ret;
	}

	/* Step 2: Read back and verify */
	ret = nvs_read(&nvs, CONFIG_ID_TEMP, &verify_buf, sizeof(verify_buf));
	if (ret < 0) {
		printk("nvs_read verify failed: %d\n", (int)ret);
		return (int)ret;
	}

	if (memcmp(new_cfg, &verify_buf, sizeof(*new_cfg)) != 0) {
		printk("CONFIG COMMIT FAILED: verify mismatch\n");
		return -EIO;
	}

	/* Step 3: Commit to primary slot */
	ret = nvs_write(&nvs, CONFIG_ID_PRIMARY, new_cfg, sizeof(*new_cfg));
	if (ret < 0) {
		printk("nvs_write primary failed: %d\n", (int)ret);
		return (int)ret;
	}

	/* Step 4: Clean up temp slot */
	ret = nvs_delete(&nvs, CONFIG_ID_TEMP);
	if (ret < 0) {
		printk("nvs_delete temp failed: %d\n", (int)ret);
	}

	printk("CONFIG COMMIT OK\n");
	return 0;
}

int main(void)
{
	int ret;
	struct app_config cfg_read;
	struct app_config new_cfg = {
		.version = 2U,
		.value   = 0xDEADBEEFU,
	};

	ret = nvs_mount(&nvs);
	if (ret < 0) {
		printk("NVS mount failed: %d\n", ret);
		return ret;
	}

	/* Check for interrupted write from previous boot */
	ssize_t rc = nvs_read(&nvs, CONFIG_ID_TEMP, &cfg_read, sizeof(cfg_read));

	if (rc > 0) {
		printk("Stale temp config found — cleaning up\n");
		nvs_delete(&nvs, CONFIG_ID_TEMP);
	}

	return atomic_config_update(&new_cfg);
}
