#include <zephyr/kernel.h>

static struct k_work my_work;

void work_handler(struct k_work *work)
{
	printk("Work executed\n");
}

void timer_expiry(struct k_timer *timer)
{
	k_work_submit(&my_work);
}

K_TIMER_DEFINE(my_timer, timer_expiry, NULL);

int main(void)
{
	k_work_init(&my_work, work_handler);

	/* One-shot: duration=1s, period=K_NO_WAIT */
	k_timer_start(&my_timer, K_MSEC(1000), K_NO_WAIT);

	k_sleep(K_SECONDS(3));
	printk("Done\n");

	return 0;
}
