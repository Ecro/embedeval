/*
 * System PM policy override to prevent deep sleep during network activity.
 * pm_policy_state_lock prevents the system from entering SUSPEND_TO_RAM.
 */

#include <zephyr/kernel.h>
#include <zephyr/pm/policy.h>

static void start_network_activity(void)
{
	/* Acquire lock: prevents PM system from choosing SUSPEND_TO_RAM */
	pm_policy_state_lock_get(PM_STATE_SUSPEND_TO_RAM, PM_ALL_SUBSTATES);
	printk("Network active — deep sleep prevented\n");
}

static void stop_network_activity(void)
{
	/* Release lock: PM system may now enter deep sleep again */
	pm_policy_state_lock_put(PM_STATE_SUSPEND_TO_RAM, PM_ALL_SUBSTATES);
	printk("Network idle — deep sleep allowed\n");
}

int main(void)
{
	printk("PM policy override demo\n");

	start_network_activity();

	/* Simulate active network period */
	k_sleep(K_MSEC(500));

	stop_network_activity();

	k_sleep(K_FOREVER);
	return 0;
}
