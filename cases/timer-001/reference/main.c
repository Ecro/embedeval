#include <zephyr/kernel.h>

static volatile int counter;

void timer_expiry(struct k_timer *timer)
{
	counter++;
}

K_TIMER_DEFINE(my_timer, timer_expiry, NULL);

int main(void)
{
	k_timer_start(&my_timer, K_MSEC(500), K_MSEC(500));

	while (1) {
		printk("Counter: %d\n", counter);
		k_sleep(K_SECONDS(2));
	}

	return 0;
}
