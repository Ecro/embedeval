#include <zephyr/kernel.h>
#include <zephyr/fs/nvs.h>
#include <zephyr/storage/flash_map.h>

#define NVS_PARTITION storage_partition
#define NVS_PARTITION_DEVICE FIXED_PARTITION_DEVICE(NVS_PARTITION)
#define NVS_PARTITION_OFFSET FIXED_PARTITION_OFFSET(NVS_PARTITION)
#define NVS_ID 1

static struct nvs_fs fs = {
	.flash_device = NVS_PARTITION_DEVICE,
	.offset = NVS_PARTITION_OFFSET,
	.sector_size = 4096,
	.sector_count = 2,
};

int main(void)
{
	int ret;
	uint32_t write_val = 0xDEADBEEF;
	uint32_t read_val = 0;

	ret = nvs_mount(&fs);
	if (ret < 0) {
		printk("NVS mount failed: %d\n", ret);
		return ret;
	}

	ret = nvs_write(&fs, NVS_ID, &write_val, sizeof(write_val));
	if (ret < 0) {
		printk("NVS write failed: %d\n", ret);
		return ret;
	}

	ret = nvs_read(&fs, NVS_ID, &read_val, sizeof(read_val));
	if (ret < 0) {
		printk("NVS read failed: %d\n", ret);
		return ret;
	}

	if (read_val == write_val) {
		printk("NVS verify OK: 0x%08x\n", read_val);
	} else {
		printk("NVS verify FAIL: wrote 0x%08x, read 0x%08x\n",
		       write_val, read_val);
		return -EIO;
	}

	return 0;
}
