/*
 * Double-buffer (ping-pong) pattern for ISR-to-thread data transfer
 * ISR fills one buffer while thread processes the other.
 * Atomic index swap ensures they never access the same buffer simultaneously.
 */

#include <zephyr/kernel.h>
#include <zephyr/sys/atomic.h>

#define BUF_SIZE 8

static uint32_t buf[2][BUF_SIZE];
static atomic_t write_idx = ATOMIC_INIT(0);
static uint32_t fill_value;

/* ISR: fills the write buffer, then atomically hands it to the thread */
static void isr_handler(const void *arg)
{
	ARG_UNUSED(arg);
	int idx = (int)atomic_get(&write_idx);

	for (int i = 0; i < BUF_SIZE; i++) {
		buf[idx][i] = fill_value + i;
	}
	fill_value += BUF_SIZE;

	/* Swap: thread now processes idx, ISR will write to (1 - idx) */
	atomic_set(&write_idx, 1 - idx);
}

/* Processor thread: reads buffer NOT being written by ISR */
static void processor_thread(void *p1, void *p2, void *p3)
{
	ARG_UNUSED(p1);
	ARG_UNUSED(p2);
	ARG_UNUSED(p3);

	for (int iter = 0; iter < 4; iter++) {
		int process_idx = 1 - (int)atomic_get(&write_idx);
		uint32_t sum = 0;

		for (int i = 0; i < BUF_SIZE; i++) {
			sum += buf[process_idx][i];
		}

		printk("iter=%d process_idx=%d sum=%u\n", iter, process_idx, sum);
		k_sleep(K_MSEC(50));
	}
}

K_THREAD_DEFINE(processor_tid, 1024,
		processor_thread, NULL, NULL, NULL,
		5, 0, 0);

int main(void)
{
	/* Simulate ISR firing 3 times */
	isr_handler(NULL);
	isr_handler(NULL);
	isr_handler(NULL);

	/* Allow processor thread to run */
	k_sleep(K_MSEC(300));

	return 0;
}
