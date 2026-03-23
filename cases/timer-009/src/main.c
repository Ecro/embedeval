#include <zephyr/kernel.h>

K_SEM_DEFINE(event_sem, 0, 1);

static void event_timer_cb(struct k_timer *timer)
{
	k_sem_give(&event_sem);
}

K_TIMER_DEFINE(event_timer, event_timer_cb, NULL);

int main(void)
{
	/* Start one-shot timer to fire after 2 seconds */
	k_timer_start(&event_timer, K_SECONDS(2), K_NO_WAIT);

	/* Wait up to 5 seconds for the event */
	int ret = k_sem_take(&event_sem, K_MSEC(5000));

	if (ret == 0) {
		printk("Event received\n");
	} else if (ret == -EAGAIN) {
		printk("Timeout: event did not arrive\n");
	} else {
		printk("Error waiting for event: %d\n", ret);
	}

	printk("Done\n");
	return 0;
}
