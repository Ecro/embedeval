#include <zephyr/kernel.h>
#include <zephyr/storage/flash_map.h>
#include <zephyr/drivers/flash.h>
#include <string.h>

#define STORAGE_PARTITION_ID FIXED_PARTITION_ID(storage_partition)
#define WRITE_DATA_SIZE      16

static int safe_flash_write(const struct flash_area *area, off_t offset,
			    const uint8_t *data, size_t size)
{
	size_t area_size = flash_area_get_size(area);

	/* Boundary validation */
	if (offset < 0) {
		printk("BOUNDARY VIOLATION: negative offset %ld\n",
		       (long)offset);
		return -EINVAL;
	}
	if (size == 0U) {
		printk("BOUNDARY VIOLATION: zero size\n");
		return -EINVAL;
	}
	if ((size_t)offset + size > area_size) {
		printk("BOUNDARY VIOLATION: offset=%ld size=%zu area=%zu\n",
		       (long)offset, size, area_size);
		return -EINVAL;
	}

	int ret = flash_area_write(area, offset, data, size);

	if (ret < 0) {
		printk("flash_area_write failed: %d\n", ret);
		return ret;
	}

	printk("WRITE OK offset=%ld size=%zu\n", (long)offset, size);
	return 0;
}

int main(void)
{
	const struct flash_area *area;
	uint8_t write_buf[WRITE_DATA_SIZE];
	size_t area_size;
	int ret;

	memset(write_buf, 0xAB, sizeof(write_buf));

	ret = flash_area_open(STORAGE_PARTITION_ID, &area);
	if (ret < 0) {
		printk("flash_area_open failed: %d\n", ret);
		return ret;
	}

	area_size = flash_area_get_size(area);
	printk("Flash area size: %zu bytes\n", area_size);

	/* Erase before write */
	ret = flash_area_erase(area, 0, flash_area_get_size(area));
	if (ret < 0) {
		printk("Erase failed: %d\n", ret);
		flash_area_close(area);
		return ret;
	}

	/* Valid write — within bounds */
	ret = safe_flash_write(area, 0, write_buf, sizeof(write_buf));
	if (ret == 0) {
		/* expected */
	} else {
		printk("Unexpected failure on valid write\n");
	}

	/* Invalid write — beyond area bounds (triggers boundary check) */
	off_t bad_offset = (off_t)(area_size - 4U);

	ret = safe_flash_write(area, bad_offset, write_buf, sizeof(write_buf));
	if (ret == -EINVAL) {
		printk("WRITE BLOCKED (boundary check worked)\n");
	}

	flash_area_close(area);
	return 0;
}
