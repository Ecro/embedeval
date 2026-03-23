#include <zephyr/kernel.h>
#include <zephyr/dfu/mcuboot.h>
#include <zephyr/dfu/dfu_target.h>
#include <zephyr/sys/reboot.h>

#define CHUNK_SIZE  256
#define TOTAL_SIZE  4096
#define NUM_CHUNKS  (TOTAL_SIZE / CHUNK_SIZE)

static uint8_t chunk[CHUNK_SIZE];

int main(void)
{
	int ret;
	int i;

	ret = dfu_target_init(DFU_TARGET_IMAGE_TYPE_MCUBOOT, 0, TOTAL_SIZE, NULL);
	if (ret < 0) {
		printk("dfu_target_init failed: %d\n", ret);
		return ret;
	}

	for (i = 0; i < NUM_CHUNKS; i++) {
		printk("Writing chunk %d/%d\n", i + 1, NUM_CHUNKS);
		ret = dfu_target_write(chunk, sizeof(chunk));
		if (ret < 0) {
			printk("dfu_target_write failed at chunk %d: %d\n", i + 1, ret);
			dfu_target_done(false);
			return ret;
		}
	}

	ret = dfu_target_done(true);
	if (ret < 0) {
		printk("dfu_target_done failed: %d\n", ret);
		return ret;
	}

	printk("DFU complete, resetting\n");
	sys_reboot(SYS_REBOOT_COLD);

	return 0;
}
