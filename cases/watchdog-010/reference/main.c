#include <zephyr/kernel.h>
#include <zephyr/task_wdt/task_wdt.h>

int main(void)
{
	int err = task_wdt_init(NULL);

	if (err < 0) {
		printk("Task WDT init failed: %d\n", err);
		return -1;
	}

	int task_wdt_id = task_wdt_add(2000, NULL, NULL);

	if (task_wdt_id < 0) {
		printk("Task WDT add failed: %d\n", task_wdt_id);
		return -1;
	}

	while (1) {
		printk("Main thread heartbeat\n");
		task_wdt_feed(task_wdt_id);
		k_sleep(K_SECONDS(1));
	}

	return 0;
}
