/*
 * PM device state query before use in Zephyr RTOS.
 * Checks state with pm_device_state_get; resumes if suspended.
 * Note: STATE enums (PM_DEVICE_STATE_*) differ from ACTION enums (PM_DEVICE_ACTION_*)
 */

#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/pm/device.h>

static int safe_device_use(const struct device *dev)
{
	enum pm_device_state state;
	int ret;

	/* Query current power state — MUST use STATE enum here */
	ret = pm_device_state_get(dev, &state);
	if (ret < 0) {
		printk("Failed to get device state: %d\n", ret);
		return ret;
	}

	if (state == PM_DEVICE_STATE_SUSPENDED) {
		printk("Resuming device\n");

		/* Resume — MUST use ACTION enum here */
		ret = pm_device_action_run(dev, PM_DEVICE_ACTION_RESUME);
		if (ret < 0) {
			printk("Failed to resume: %d\n", ret);
			return ret;
		}
	} else {
		/* Device already active — PM_DEVICE_STATE_ACTIVE */
		printk("Device already active\n");
	}

	/* Now safe to use the device */
	printk("Using device\n");

	return 0;
}

int main(void)
{
	/* NULL device used for demonstration — in production: DEVICE_DT_GET(...) */
	const struct device *dev = NULL;

	printk("PM device state query demo\n");

	/* First call: device may be suspended */
	safe_device_use(dev);

	/* Second call: device is now active */
	safe_device_use(dev);

	return 0;
}
