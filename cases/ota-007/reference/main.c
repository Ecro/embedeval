#include <zephyr/kernel.h>
#include <zephyr/dfu/dfu_target.h>

#define CHUNK_SIZE        256
#define TOTAL_IMAGE_SIZE  65536

static uint8_t chunk[CHUNK_SIZE];

static void report_progress(size_t received, size_t total)
{
	if (total == 0) {
		printk("Progress: unknown (total size not set)\n");
		return;
	}

	uint8_t pct = (uint8_t)((received * 100U) / total);

	printk("OTA progress: %u%%\n", (unsigned int)pct);
}

static int ota_download(void)
{
	int ret;
	size_t bytes_received = 0;
	size_t num_chunks = TOTAL_IMAGE_SIZE / CHUNK_SIZE;

	ret = dfu_target_init(DFU_TARGET_IMAGE_TYPE_MCUBOOT, 0, TOTAL_IMAGE_SIZE, NULL);
	if (ret < 0) {
		printk("dfu_target_init failed: %d\n", ret);
		return ret;
	}

	for (size_t i = 0; i < num_chunks; i++) {
		ret = dfu_target_write(chunk, CHUNK_SIZE);
		if (ret < 0) {
			printk("dfu_target_write failed at chunk %zu: %d\n", i + 1, ret);
			dfu_target_done(false);
			return ret;
		}

		bytes_received += CHUNK_SIZE;
		report_progress(bytes_received, TOTAL_IMAGE_SIZE);
	}

	ret = dfu_target_done(true);
	if (ret < 0) {
		printk("dfu_target_done failed: %d\n", ret);
		return ret;
	}

	return 0;
}

int main(void)
{
	int ret;

	printk("OTA progress reporting demo\n");

	ret = ota_download();
	if (ret < 0) {
		printk("OTA download failed: %d\n", ret);
		return ret;
	}

	printk("OTA download complete\n");
	k_sleep(K_FOREVER);
	return 0;
}
