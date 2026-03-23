#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/pm/device.h>
#include <zephyr/pm/device_runtime.h>

static int my_pm_action(const struct device *dev,
			enum pm_device_action action)
{
	switch (action) {
	case PM_DEVICE_ACTION_SUSPEND:
		printk("Runtime: suspended\n");
		return 0;
	case PM_DEVICE_ACTION_RESUME:
		printk("Runtime: resumed\n");
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

	ret = pm_device_runtime_enable(dev);
	if (ret < 0) {
		printk("Failed to enable runtime PM: %d\n", ret);
		return ret;
	}
	printk("Runtime PM enabled\n");

	ret = pm_device_runtime_get(dev);
	if (ret < 0) {
		printk("Failed to get device: %d\n", ret);
		pm_device_runtime_disable(dev);
		return ret;
	}
	printk("Got device reference\n");

	printk("Doing work with device\n");

	ret = pm_device_runtime_put(dev);
	if (ret < 0) {
		printk("Failed to put device: %d\n", ret);
	}
	printk("Released device reference\n");

	pm_device_runtime_disable(dev);
	printk("Runtime PM disabled\n");

	return 0;
}
