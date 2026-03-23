#include <zephyr/kernel.h>
#include <zephyr/pm/device.h>

typedef enum {
	DEV_STATE_ACTIVE,
	DEV_STATE_SUSPENDED,
} dev_state_t;

static dev_state_t current_state = DEV_STATE_ACTIVE;

static int my_pm_action(const struct device *dev,
			enum pm_device_action action)
{
	switch (action) {
	case PM_DEVICE_ACTION_SUSPEND:
		if (current_state == DEV_STATE_SUSPENDED) {
			return -EALREADY;
		}
		current_state = DEV_STATE_SUSPENDED;
		printk("Device suspended\n");
		return 0;

	case PM_DEVICE_ACTION_RESUME:
		if (current_state == DEV_STATE_ACTIVE) {
			return -EALREADY;
		}
		current_state = DEV_STATE_ACTIVE;
		printk("Device resumed\n");
		return 0;

	default:
		return -ENOTSUP;
	}
}

int main(void)
{
	int ret;

	ret = my_pm_action(NULL, PM_DEVICE_ACTION_SUSPEND);
	printk("Suspend 1: %d\n", ret);

	ret = my_pm_action(NULL, PM_DEVICE_ACTION_SUSPEND);
	printk("Suspend 2 (duplicate): %d\n", ret);

	ret = my_pm_action(NULL, PM_DEVICE_ACTION_RESUME);
	printk("Resume: %d\n", ret);

	return 0;
}
