/*
 * Peripheral power gating using Zephyr PM device API.
 * Clock disabled when idle, re-enabled before next access.
 */

#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/pm/device.h>

/* Mock device — in production use DEVICE_DT_GET(DT_NODELABEL(mydev)) */
static const struct device *dev;
static bool peripheral_active = false;

static int peripheral_use(void)
{
	int ret;

	/* Only resume if currently suspended */
	if (!peripheral_active) {
		ret = pm_device_action_run(dev, PM_DEVICE_ACTION_RESUME);
		if (ret < 0 && ret != -EALREADY) {
			printk("Failed to resume peripheral: %d\n", ret);
			return ret;
		}
		peripheral_active = true;
	}

	/* Use the peripheral */
	printk("Using peripheral\n");

	/* Suspend after use to save power */
	ret = pm_device_action_run(dev, PM_DEVICE_ACTION_SUSPEND);
	if (ret < 0 && ret != -EALREADY) {
		printk("Failed to suspend peripheral: %d\n", ret);
		return ret;
	}
	peripheral_active = false;

	return 0;
}

int main(void)
{
	printk("Peripheral power gating demo\n");

	/* Demonstrate periodic use with power gating between uses */
	for (int i = 0; i < 5; i++) {
		int ret = peripheral_use();

		if (ret < 0) {
			printk("peripheral_use failed: %d\n", ret);
		}

		/* Peripheral is now suspended — saving power during sleep */
		k_sleep(K_MSEC(1000));
	}

	return 0;
}
