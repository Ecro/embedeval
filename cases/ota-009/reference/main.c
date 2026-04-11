#include <zephyr/kernel.h>
#include <zephyr/dfu/mcuboot.h>
#include <zephyr/sys/printk.h>

static int self_test(void)
{
	/* Stub: production code would verify peripherals, ROM checksums,
	 * configuration integrity, and key hardware subsystems. */
	return 0;
}

int main(void)
{
	if (boot_is_img_confirmed()) {
		printk("already confirmed\n");
		return 0;
	}

	if (self_test() != 0) {
		/* Leave the image unconfirmed — MCUboot will restore the
		 * previous working image on the next reboot. */
		printk("rollback pending\n");
		return 0;
	}

	int ret = boot_write_img_confirmed();

	if (ret != 0) {
		printk("boot_write_img_confirmed failed: %d\n", ret);
		return ret;
	}

	printk("confirmed ok\n");
	return 0;
}
