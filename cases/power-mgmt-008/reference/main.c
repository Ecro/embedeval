/*
 * Wake timer from deep sleep in Zephyr RTOS.
 * Timer armed BEFORE pm_state_force — ensures wakeup source is ready.
 */

#include <zephyr/kernel.h>
#include <zephyr/pm/pm.h>

#define SLEEP_DURATION_MS  2000U
#define WAKEUP_TIMER_MS    1500U  /* Must be < SLEEP_DURATION_MS */

static struct k_timer wakeup_timer;

static void wakeup_timer_cb(struct k_timer *t)
{
	ARG_UNUSED(t);
	printk("Wakeup timer fired\n");
}

int main(void)
{
	k_timer_init(&wakeup_timer, wakeup_timer_cb, NULL);

	/* Arm the timer BEFORE entering deep sleep */
	k_timer_start(&wakeup_timer, K_MSEC(WAKEUP_TIMER_MS), K_NO_WAIT);

	printk("Entering deep sleep, wakeup in %d ms\n", WAKEUP_TIMER_MS);

	/* Force system into SUSPEND_TO_RAM deep sleep */
	pm_state_force(0, &(struct pm_state_info){PM_STATE_SUSPEND_TO_RAM, 0, 0});

	/* Execution resumes here after wakeup */
	printk("Returned from deep sleep\n");

	/* Clean up timer */
	k_timer_stop(&wakeup_timer);

	k_sleep(K_FOREVER);
	return 0;
}
