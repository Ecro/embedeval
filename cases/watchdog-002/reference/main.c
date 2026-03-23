#include <zephyr/kernel.h>
#include <zephyr/task_wdt/task_wdt.h>

static int wdt_channel_id;

K_THREAD_STACK_DEFINE(worker_stack, 512);
static struct k_thread worker_thread;

void worker_fn(void *p1, void *p2, void *p3)
{
	while (1) {
		printk("Worker running\n");
		task_wdt_feed(wdt_channel_id);
		k_sleep(K_SECONDS(1));
	}
}

int main(void)
{
	int err = task_wdt_init(NULL);

	if (err != 0) {
		printk("Task WDT init failed: %d\n", err);
		return -1;
	}

	wdt_channel_id = task_wdt_add(3000, NULL, NULL);
	if (wdt_channel_id < 0) {
		printk("Task WDT add failed: %d\n", wdt_channel_id);
		return -1;
	}

	k_thread_create(&worker_thread, worker_stack,
			K_THREAD_STACK_SIZEOF(worker_stack),
			worker_fn, NULL, NULL, NULL,
			5, 0, K_NO_WAIT);

	k_sleep(K_FOREVER);

	return 0;
}
