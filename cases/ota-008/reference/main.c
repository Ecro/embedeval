#include <zephyr/kernel.h>
#include <zephyr/dfu/mcuboot.h>
#include <zephyr/sys/reboot.h>
#include <errno.h>

#define CONFIRM_TIMEOUT_MS  60000

static int self_test(void)
{
	printk("Running self-test...\n");
	/* Real application: verify peripherals, connectivity, configuration */
	return 0;
}

int main(void)
{
	int ret;

	if (!boot_is_img_confirmed()) {
		printk("Unconfirmed image detected — starting confirm window\n");

		int64_t deadline = k_uptime_get() + CONFIRM_TIMEOUT_MS;

		ret = self_test();
		if (ret != 0) {
			printk("Self-test FAILED (%d) — resetting for rollback\n", ret);
			sys_reboot(SYS_REBOOT_COLD);
			/* unreachable */
		}

		if (k_uptime_get() > deadline) {
			printk("Rollback timeout — resetting\n");
			sys_reboot(SYS_REBOOT_COLD);
			/* unreachable */
		}

		ret = boot_write_img_confirmed();
		if (ret < 0) {
			printk("boot_write_img_confirmed failed (%d) — resetting\n", ret);
			sys_reboot(SYS_REBOOT_COLD);
			/* unreachable */
		}

		printk("Image confirmed successfully\n");
	} else {
		printk("Image already confirmed — running application\n");
	}

	printk("Application running normally\n");
	while (1) {
		k_sleep(K_MSEC(1000));
		printk("Heartbeat\n");
	}

	return 0;
}
