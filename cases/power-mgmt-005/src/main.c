#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/pm/device.h>

static bool dev_a_suspended;
static bool dev_b_suspended;
static bool dev_c_suspended;

static int my_pm_action(const struct device *dev,
			enum pm_device_action action)
{
	switch (action) {
	case PM_DEVICE_ACTION_SUSPEND:
		printk("device %s suspended\n", dev->name);
		return 0;
	case PM_DEVICE_ACTION_RESUME:
		printk("device %s resumed\n", dev->name);
		return 0;
	default:
		return -ENOTSUP;
	}
}

static const struct device *dev_a = DEVICE_DT_GET(DT_NODELABEL(dev_a));
static const struct device *dev_b = DEVICE_DT_GET(DT_NODELABEL(dev_b));
static const struct device *dev_c = DEVICE_DT_GET(DT_NODELABEL(dev_c));

static int suspend_all(void)
{
	int ret;

	/* Suspend in dependency order: c (most dependent) first */
	ret = pm_device_action_run(dev_c, PM_DEVICE_ACTION_SUSPEND);
	if (ret < 0) {
		printk("Failed to suspend dev_c: %d\n", ret);
		return ret;
	}
	dev_c_suspended = true;

	ret = pm_device_action_run(dev_b, PM_DEVICE_ACTION_SUSPEND);
	if (ret < 0) {
		printk("Failed to suspend dev_b: %d, rolling back\n", ret);
		pm_device_action_run(dev_c, PM_DEVICE_ACTION_RESUME);
		dev_c_suspended = false;
		return ret;
	}
	dev_b_suspended = true;

	ret = pm_device_action_run(dev_a, PM_DEVICE_ACTION_SUSPEND);
	if (ret < 0) {
		printk("Failed to suspend dev_a: %d, rolling back\n", ret);
		pm_device_action_run(dev_b, PM_DEVICE_ACTION_RESUME);
		dev_b_suspended = false;
		pm_device_action_run(dev_c, PM_DEVICE_ACTION_RESUME);
		dev_c_suspended = false;
		return ret;
	}
	dev_a_suspended = true;

	return 0;
}

static int resume_all(void)
{
	int ret;

	/* Resume in reverse order: a (least dependent) first */
	if (dev_a_suspended) {
		ret = pm_device_action_run(dev_a, PM_DEVICE_ACTION_RESUME);
		if (ret < 0) {
			printk("Failed to resume dev_a: %d\n", ret);
			return ret;
		}
		dev_a_suspended = false;
	}

	if (dev_b_suspended) {
		ret = pm_device_action_run(dev_b, PM_DEVICE_ACTION_RESUME);
		if (ret < 0) {
			printk("Failed to resume dev_b: %d\n", ret);
			return ret;
		}
		dev_b_suspended = false;
	}

	if (dev_c_suspended) {
		ret = pm_device_action_run(dev_c, PM_DEVICE_ACTION_RESUME);
		if (ret < 0) {
			printk("Failed to resume dev_c: %d\n", ret);
			return ret;
		}
		dev_c_suspended = false;
	}

	return 0;
}

int main(void)
{
	int ret;

	ret = suspend_all();
	printk("suspend_all: %d\n", ret);

	ret = resume_all();
	printk("resume_all: %d\n", ret);

	return 0;
}
