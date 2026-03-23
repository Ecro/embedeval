#include <zephyr/kernel.h>
#include <zephyr/storage/flash_map.h>

#define SECTOR_SIZE 4096

int main(void)
{
	const struct flash_area *fa;
	int ret;
	uint32_t write_val = 0xCAFEBABEU;
	uint32_t read_val = 0U;

	ret = flash_area_open(FIXED_PARTITION_ID(storage_partition), &fa);
	if (ret < 0) {
		printk("flash_area_open failed: %d\n", ret);
		return ret;
	}

	ret = flash_area_erase(fa, 0, SECTOR_SIZE);
	if (ret < 0) {
		printk("flash_area_erase failed: %d\n", ret);
		flash_area_close(fa);
		return ret;
	}

	ret = flash_area_write(fa, 0, &write_val, sizeof(write_val));
	if (ret < 0) {
		printk("flash_area_write failed: %d\n", ret);
		flash_area_close(fa);
		return ret;
	}

	ret = flash_area_read(fa, 0, &read_val, sizeof(read_val));
	if (ret < 0) {
		printk("flash_area_read failed: %d\n", ret);
		flash_area_close(fa);
		return ret;
	}

	flash_area_close(fa);

	if (read_val == write_val) {
		printk("Flash verify OK: 0x%08x\n", read_val);
	} else {
		printk("Flash verify FAIL: wrote 0x%08x, read 0x%08x\n",
		       write_val, read_val);
		return -EIO;
	}

	return 0;
}
