/*
 * ISR-safe FIFO using k_fifo for ISR-to-thread data transfer.
 * Items are statically allocated — no heap usage in ISR.
 */

#include <zephyr/kernel.h>

#define POOL_SIZE 8

/* Data item: fifo_reserved MUST be first member for k_fifo linked list */
struct data_item {
	void *fifo_reserved;
	uint32_t value;
};

/* Static pool avoids k_malloc in ISR context */
static struct data_item item_pool[POOL_SIZE];
static uint32_t pool_idx;

K_FIFO_DEFINE(my_fifo);

/* Simulated ISR — called from interrupt context */
static void my_isr_handler(const void *arg)
{
	ARG_UNUSED(arg);

	/* Take next item from static pool (wrap around) */
	struct data_item *item = &item_pool[pool_idx % POOL_SIZE];
	pool_idx++;

	item->value = k_cycle_get_32();

	/* k_fifo_put is ISR-safe and non-blocking */
	k_fifo_put(&my_fifo, item);
}

#define CONSUMER_STACK_SIZE 1024
#define CONSUMER_PRIORITY   7

static void consumer_thread(void *p1, void *p2, void *p3)
{
	ARG_UNUSED(p1);
	ARG_UNUSED(p2);
	ARG_UNUSED(p3);

	while (1) {
		/* k_fifo_get blocks until an item is available */
		struct data_item *item = k_fifo_get(&my_fifo, K_FOREVER);

		if (item != NULL) {
			printk("Received value: %u\n", item->value);
		}
	}
}

K_THREAD_DEFINE(consumer_tid, CONSUMER_STACK_SIZE,
		consumer_thread, NULL, NULL, NULL,
		CONSUMER_PRIORITY, 0, 0);

int main(void)
{
	printk("ISR FIFO demo started\n");

	/* Trigger ISR manually for demonstration */
	my_isr_handler(NULL);

	k_sleep(K_FOREVER);
	return 0;
}
