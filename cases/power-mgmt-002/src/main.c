#include <zephyr/kernel.h>

int main(void)
{
	int64_t t_before, t_after, elapsed;

	t_before = k_uptime_get();
	printk("Before sleep: uptime=%lld ms\n", t_before);

	k_sleep(K_MSEC(1000));

	t_after = k_uptime_get();
	printk("After sleep: uptime=%lld ms\n", t_after);

	elapsed = t_after - t_before;
	printk("Elapsed: %lld ms\n", elapsed);

	return 0;
}
