#include <zephyr/kernel.h>

int main(void)
{
	while (1) {
		int64_t uptime = k_uptime_get();

		printk("Uptime: %lld ms\n", uptime);
		k_sleep(K_SECONDS(2));
	}

	return 0;
}
