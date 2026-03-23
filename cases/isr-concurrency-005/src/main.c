/*
 * ISR-deferred processing with k_work
 * ISR: minimal — increments counter + submits work
 * Work handler: runs in system work queue thread context (safe for heavy ops)
 */

#include <zephyr/kernel.h>
#include <zephyr/sys/atomic.h>

static struct k_work my_work;
static atomic_t isr_event_count = ATOMIC_INIT(0);

/* Work handler: runs in thread context — safe for printk, malloc, etc. */
static void work_handler(struct k_work *work)
{
	ARG_UNUSED(work);
	int events = (int)atomic_get(&isr_event_count);

	printk("work_handler: events=%d\n", events);

	/* Simulate heavy processing */
	for (int i = 0; i < 4; i++) {
		printk("  processing step %d\n", i);
	}
}

/* ISR: minimal — only update counter and submit deferred work */
static void isr_handler(const void *arg)
{
	ARG_UNUSED(arg);

	atomic_inc(&isr_event_count);

	/* Submit work to system work queue — safe from ISR */
	k_work_submit(&my_work);
}

int main(void)
{
	/* k_work_init MUST be called before ISR fires */
	k_work_init(&my_work, work_handler);

	/* Simulate ISR firing 3 times */
	isr_handler(NULL);
	isr_handler(NULL);
	isr_handler(NULL);

	/* Allow work queue to drain */
	k_sleep(K_MSEC(200));

	return 0;
}
