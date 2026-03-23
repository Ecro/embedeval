#include <zephyr/kernel.h>
#include <zephyr/drivers/flash.h>
#include <zephyr/storage/flash_map.h>
#include <string.h>

#define STORAGE_PARTITION    storage_partition
#define STORAGE_DEVICE       FIXED_PARTITION_DEVICE(STORAGE_PARTITION)
#define STORAGE_OFFSET       FIXED_PARTITION_OFFSET(STORAGE_PARTITION)

#define NUM_SECTORS     2
#define SECTOR_SIZE     4096U
#define WRITE_THRESHOLD 100
#define DATA_SIZE       16

static uint32_t write_count[NUM_SECTORS];
static uint32_t current_sector;

static int wear_write(const struct device *flash_dev,
		      const uint8_t *data, size_t len)
{
	int ret;
	off_t sector_offset;

	/* Rotate to next sector if write threshold reached */
	if (write_count[current_sector] >= WRITE_THRESHOLD) {
		current_sector = (current_sector + 1U) % NUM_SECTORS;
		sector_offset = (off_t)(STORAGE_OFFSET
					+ current_sector * SECTOR_SIZE);

		ret = flash_erase(flash_dev, sector_offset, SECTOR_SIZE);
		if (ret < 0) {
			printk("WEAR WRITE FAILED: erase sector %u: %d\n",
			       current_sector, ret);
			return ret;
		}
		write_count[current_sector] = 0U;
	}

	sector_offset = (off_t)(STORAGE_OFFSET + current_sector * SECTOR_SIZE);
	off_t write_offset = sector_offset
			     + (off_t)(write_count[current_sector] * DATA_SIZE);

	ret = flash_write(flash_dev, write_offset, data, len);
	if (ret < 0) {
		printk("WEAR WRITE FAILED: write sector %u: %d\n",
		       current_sector, ret);
		return ret;
	}

	write_count[current_sector]++;
	printk("WEAR WRITE OK sector=%u count=%u\n",
	       current_sector, write_count[current_sector]);
	return 0;
}

int main(void)
{
	const struct device *flash_dev = STORAGE_DEVICE;
	uint8_t data_a[DATA_SIZE] = {0xAA};
	uint8_t data_b[DATA_SIZE] = {0xBB};
	uint8_t data_c[DATA_SIZE] = {0xCC};

	if (!device_is_ready(flash_dev)) {
		printk("Flash device not ready\n");
		return -1;
	}

	/* Erase first sector before initial use */
	int ret = flash_erase(flash_dev, STORAGE_OFFSET, SECTOR_SIZE);

	if (ret < 0) {
		printk("Initial erase failed: %d\n", ret);
		return ret;
	}

	wear_write(flash_dev, data_a, sizeof(data_a));
	wear_write(flash_dev, data_b, sizeof(data_b));
	wear_write(flash_dev, data_c, sizeof(data_c));

	return 0;
}
