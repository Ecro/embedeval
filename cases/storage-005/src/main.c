#include <zephyr/kernel.h>
#include <zephyr/fs/nvs.h>
#include <zephyr/storage/flash_map.h>
#include <errno.h>

#define NVS_PARTITION        storage_partition
#define NVS_PARTITION_DEVICE FIXED_PARTITION_DEVICE(NVS_PARTITION)
#define NVS_PARTITION_OFFSET FIXED_PARTITION_OFFSET(NVS_PARTITION)

#define NVS_ID_A 1
#define NVS_ID_B 2
#define NVS_ID_C 3

static struct nvs_fs fs = {
	.flash_device = NVS_PARTITION_DEVICE,
	.offset = NVS_PARTITION_OFFSET,
	.sector_size = 4096,
	.sector_count = 2,
};

int main(void)
{
	int ret;
	ssize_t free_space;
	uint32_t val_a = 0x11111111U;
	uint32_t val_b = 0x22222222U;
	uint32_t val_c = 0x33333333U;

	ret = nvs_mount(&fs);
	if (ret < 0) {
		printk("NVS mount failed: %d\n", ret);
		return ret;
	}

	ret = nvs_write(&fs, NVS_ID_A, &val_a, sizeof(val_a));
	if (ret < 0) {
		printk("NVS write A failed: %d\n", ret);
		return ret;
	}

	ret = nvs_write(&fs, NVS_ID_B, &val_b, sizeof(val_b));
	if (ret < 0) {
		printk("NVS write B failed: %d\n", ret);
		return ret;
	}

	ret = nvs_write(&fs, NVS_ID_C, &val_c, sizeof(val_c));
	if (ret < 0) {
		printk("NVS write C failed: %d\n", ret);
		return ret;
	}

	free_space = nvs_calc_free_space(&fs);
	if (free_space < 0) {
		printk("nvs_calc_free_space failed: %d\n", (int)free_space);
		return (int)free_space;
	}
	printk("Free space after writes: %zu bytes\n", (size_t)free_space);

	ret = nvs_delete(&fs, NVS_ID_A);
	if (ret < 0) {
		printk("NVS delete failed: %d\n", ret);
		return ret;
	}

	free_space = nvs_calc_free_space(&fs);
	if (free_space < 0) {
		printk("nvs_calc_free_space failed: %d\n", (int)free_space);
		return (int)free_space;
	}
	printk("Free space after delete: %zu bytes\n", (size_t)free_space);

	/* Demonstrate ENOSPC handling: fill until no space remains */
	for (uint16_t id = 10U; id < 200U; id++) {
		uint32_t fill_val = (uint32_t)id;

		if (free_space < (ssize_t)sizeof(fill_val)) {
			printk("Insufficient space, skipping write id=%u\n", id);
			break;
		}

		ret = nvs_write(&fs, id, &fill_val, sizeof(fill_val));
		if (ret == -ENOSPC) {
			printk("NVS full (ENOSPC) at id=%u, handled gracefully\n", id);
			break;
		} else if (ret < 0) {
			printk("NVS write id=%u failed: %d\n", id, ret);
			return ret;
		}

		free_space = nvs_calc_free_space(&fs);
		if (free_space < 0) {
			break;
		}
	}

	printk("NVS wear-leveling demo complete\n");
	return 0;
}
