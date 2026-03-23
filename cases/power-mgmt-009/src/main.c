/*
 * Battery-aware PM transitions for Zephyr RTOS.
 * Reads battery ADC level and adjusts sleep policy accordingly.
 */

#include <zephyr/kernel.h>
#include <zephyr/drivers/adc.h>
#include <zephyr/pm/policy.h>

#define LOW_BATTERY_THRESHOLD 20  /* percent */

/* Simulated battery ADC readings (descending to show threshold crossing) */
static const int battery_samples[] = {100, 80, 50, 15, 10};
static int sample_idx;

static int read_battery_percent(void)
{
	if (sample_idx >= (int)ARRAY_SIZE(battery_samples)) {
		return battery_samples[ARRAY_SIZE(battery_samples) - 1];
	}
	return battery_samples[sample_idx++];
}

static void apply_pm_policy(int battery_pct)
{
	if (battery_pct <= LOW_BATTERY_THRESHOLD) {
		printk("Low battery (%d%%), entering aggressive sleep\n", battery_pct);
		/* Force deepest available sleep state */
		pm_state_force(0, &(struct pm_state_info){PM_STATE_SUSPEND_TO_RAM, 0, 0});
	} else {
		printk("Battery OK (%d%%), normal PM\n", battery_pct);
		/* Normal operation — allow light sleep only */
		pm_state_force(0, &(struct pm_state_info){PM_STATE_SUSPEND_TO_IDLE, 0, 0});
	}
}

int main(void)
{
	printk("Battery-aware PM demo\n");

	while (1) {
		/* Read battery BEFORE making PM decision */
		int pct = read_battery_percent();

		apply_pm_policy(pct);

		k_sleep(K_MSEC(500));
	}

	return 0;
}
