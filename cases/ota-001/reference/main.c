#include <zephyr/kernel.h>
#include <zephyr/dfu/mcuboot.h>

static int self_test(void)
{
	/* Basic self-test: verify critical system state */
	printk("Running self-test...\n");
	/* In real application: check peripherals, config, connectivity */
	return 0; /* 0 = pass */
}

int main(void)
{
	int ret;

	if (!boot_is_img_confirmed()) {
		printk("Unconfirmed image — running self-test\n");

		ret = self_test();
		if (ret != 0) {
			printk("Self-test FAILED (%d) — will rollback\n", ret);
			return ret;
		}

		ret = boot_write_img_confirmed();
		if (ret < 0) {
			printk("Image confirm failed: %d\n", ret);
			return ret;
		}
		printk("Image confirmed successfully\n");
	} else {
		printk("Image already confirmed\n");
	}

	printk("Application running normally\n");
	k_sleep(K_FOREVER);
	return 0;
}
