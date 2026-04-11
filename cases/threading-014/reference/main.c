#include <zephyr/kernel.h>
#include <zephyr/sys/printk.h>

static volatile int shared_value;
static volatile int ready_flag;

static void producer_entry(void *p1, void *p2, void *p3)
{
	ARG_UNUSED(p1);
	ARG_UNUSED(p2);
	ARG_UNUSED(p3);

	shared_value = 42;
	/* Prevent the compiler from reordering the flag store ahead of
	 * the data store — the consumer relies on seeing data before flag. */
	compiler_barrier();
	ready_flag = 1;
}

static void consumer_entry(void *p1, void *p2, void *p3)
{
	ARG_UNUSED(p1);
	ARG_UNUSED(p2);
	ARG_UNUSED(p3);

	while (ready_flag == 0) {
		k_yield();
	}
	compiler_barrier();
	printk("value=%d\n", shared_value);
}

K_THREAD_DEFINE(producer_tid, 1024, producer_entry, NULL, NULL, NULL,
		5, 0, 0);
K_THREAD_DEFINE(consumer_tid, 1024, consumer_entry, NULL, NULL, NULL,
		6, 0, 0);

int main(void)
{
	k_sleep(K_FOREVER);
	return 0;
}
