/*
 * prj.conf:
 * CONFIG_THREAD_ANALYZER=y
 * CONFIG_THREAD_ANALYZER_USE_PRINTK=y
 * CONFIG_THREAD_NAME=y
 */

#include <zephyr/kernel.h>
#include <zephyr/debug/thread_analyzer.h>

K_THREAD_STACK_DEFINE(worker_stack, 512);
static struct k_thread worker_thread;

static void worker_fn(void *p1, void *p2, void *p3)
{
	ARG_UNUSED(p1);
	ARG_UNUSED(p2);
	ARG_UNUSED(p3);

	volatile int sum = 0;

	for (int i = 0; i < 1000; i++)
		sum += i;

	printk("Worker done, sum=%d\n", sum);
	k_sleep(K_FOREVER);
}

int main(void)
{
	k_thread_create(&worker_thread, worker_stack,
			K_THREAD_STACK_SIZEOF(worker_stack),
			worker_fn, NULL, NULL, NULL,
			5, 0, K_NO_WAIT);

	k_thread_name_set(&worker_thread, "worker");

	/* Let threads run before sampling stack usage */
	k_sleep(K_MSEC(100));

	thread_analyzer_print();
	printk("Stack analysis complete\n");

	return 0;
}
