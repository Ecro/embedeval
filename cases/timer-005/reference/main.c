#include <zephyr/kernel.h>

static atomic_t fast_count;
static atomic_t mid_count;
static atomic_t slow_count;

void fast_expiry(struct k_timer *timer)
{
	atomic_inc(&fast_count);
}

void mid_expiry(struct k_timer *timer)
{
	atomic_inc(&mid_count);
}

void slow_expiry(struct k_timer *timer)
{
	atomic_inc(&slow_count);
}

K_TIMER_DEFINE(fast_timer, fast_expiry, NULL);
K_TIMER_DEFINE(mid_timer, mid_expiry, NULL);
K_TIMER_DEFINE(slow_timer, slow_expiry, NULL);

int main(void)
{
	k_timer_start(&fast_timer, K_MSEC(100), K_MSEC(100));
	k_timer_start(&mid_timer, K_MSEC(250), K_MSEC(250));
	k_timer_start(&slow_timer, K_MSEC(1000), K_MSEC(1000));

	for (int i = 0; i < 5; i++) {
		k_sleep(K_SECONDS(2));
		printk("fast=%ld mid=%ld slow=%ld\n",
		       (long)atomic_get(&fast_count),
		       (long)atomic_get(&mid_count),
		       (long)atomic_get(&slow_count));
	}

	return 0;
}
