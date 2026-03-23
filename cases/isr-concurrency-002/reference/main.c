/*
 * ISR-to-thread communication via k_msgq
 * ISR uses K_NO_WAIT (never blocks), thread uses K_FOREVER (waits for data)
 */

#include <zephyr/kernel.h>

struct sensor_msg {
	uint32_t sensor_val;
};

K_MSGQ_DEFINE(sensor_msgq, sizeof(struct sensor_msg), 8, 4);

static uint32_t isr_counter;

/* Simulated ISR: must use K_NO_WAIT, no blocking calls */
static void isr_handler(const void *arg)
{
	ARG_UNUSED(arg);
	struct sensor_msg msg = {
		.sensor_val = isr_counter++,
	};

	/* K_NO_WAIT: never block in ISR context */
	k_msgq_put(&sensor_msgq, &msg, K_NO_WAIT);
}

/* Consumer thread: blocks on queue with K_FOREVER */
static void consumer_thread(void *p1, void *p2, void *p3)
{
	ARG_UNUSED(p1);
	ARG_UNUSED(p2);
	ARG_UNUSED(p3);

	struct sensor_msg msg;

	while (true) {
		k_msgq_get(&sensor_msgq, &msg, K_FOREVER);
		printk("Received: sensor_val=%u\n", msg.sensor_val);
	}
}

K_THREAD_DEFINE(consumer_tid, 1024,
		consumer_thread, NULL, NULL, NULL,
		5, 0, 0);

int main(void)
{
	/* Simulate ISR firing 3 times */
	isr_handler(NULL);
	isr_handler(NULL);
	isr_handler(NULL);

	/* Allow consumer thread to process messages */
	k_sleep(K_MSEC(100));

	return 0;
}
