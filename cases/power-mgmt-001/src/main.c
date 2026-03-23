#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/pm/device.h>

static int my_pm_action(const struct device *dev,
			enum pm_device_action action)
{
	switch (action) {
	case PM_DEVICE_ACTION_SUSPEND:
		printk("Device suspended\n");
		return 0;
	case PM_DEVICE_ACTION_RESUME:
		printk("Device resumed\n");
		return 0;
	default:
		return -ENOTSUP;
	}
}

int main(void)
{
	const struct device *dev = DEVICE_DT_GET(DT_NODELABEL(my_dev));
	int ret;

	if (!device_is_ready(dev)) {
		printk("Device not ready\n");
		return -ENODEV;
	}

	ret = pm_device_action_run(dev, PM_DEVICE_ACTION_SUSPEND);
	if (ret < 0 && ret != -EALREADY) {
		printk("Suspend failed: %d\n", ret);
		return ret;
	}
	printk("Suspend OK\n");

	ret = pm_device_action_run(dev, PM_DEVICE_ACTION_RESUME);
	if (ret < 0 && ret != -EALREADY) {
		printk("Resume failed: %d\n", ret);
		return ret;
	}
	printk("Resume OK\n");

	return 0;
}
