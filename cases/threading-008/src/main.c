/*
 * Real-time thread with 10ms deadline measurement in Zephyr RTOS.
 * Uses k_cycle_get_32 for high-resolution timing.
 */

#include <zephyr/kernel.h>

#define DEADLINE_US    10000U  /* 10 ms deadline */
#define RT_PRIORITY    2       /* High priority (< 5) */
#define RT_STACK_SIZE  1024

/* Simulated real-time work — deterministic computation, no blocking */
static void do_work(void)
{
	volatile uint32_t sum = 0;

	for (uint32_t i = 0; i < 1000; i++) {
		sum += i;
	}

	/* Prevent compiler from optimizing away the loop */
	(void)sum;
}

static void rt_thread(void *p1, void *p2, void *p3)
{
	ARG_UNUSED(p1);
	ARG_UNUSED(p2);
	ARG_UNUSED(p3);

	while (1) {
		uint32_t t0 = k_cycle_get_32();

		do_work();

		uint32_t t1 = k_cycle_get_32();
		uint32_t cycles = t1 - t0;
		uint32_t us = k_cyc_to_us_near32(cycles);

		if (us > DEADLINE_US) {
			printk("DEADLINE MISSED: %u us (limit=%u us)\n", us, DEADLINE_US);
		} else {
			printk("Work completed in %u us (deadline=%u us)\n", us, DEADLINE_US);
		}

		/* Wait before next iteration */
		k_sleep(K_MSEC(100));
	}
}

K_THREAD_DEFINE(rt_tid, RT_STACK_SIZE,
		rt_thread, NULL, NULL, NULL,
		RT_PRIORITY, 0, 0);

int main(void)
{
	printk("Real-time deadline demo started\n");
	k_sleep(K_FOREVER);
	return 0;
}
