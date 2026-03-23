#include <zephyr/kernel.h>

K_MUTEX_DEFINE(prio_mutex);

void low_prio_entry(void *p1, void *p2, void *p3)
{
	k_mutex_lock(&prio_mutex, K_FOREVER);
	printk("Low: holding mutex\n");
	k_sleep(K_MSEC(300));
	printk("Low: releasing mutex\n");
	k_mutex_unlock(&prio_mutex);
}

void med_prio_entry(void *p1, void *p2, void *p3)
{
	k_sleep(K_MSEC(50));
	printk("Med: running (should not preempt low)\n");
	while (1) {
		k_sleep(K_MSEC(100));
	}
}

void high_prio_entry(void *p1, void *p2, void *p3)
{
	k_sleep(K_MSEC(100));
	k_mutex_lock(&prio_mutex, K_FOREVER);
	printk("High: acquired mutex\n");
	k_mutex_unlock(&prio_mutex);
}

K_THREAD_DEFINE(low_prio_thread,  1024, low_prio_entry,  NULL, NULL, NULL, 10, 0, 0);
K_THREAD_DEFINE(med_prio_thread,  1024, med_prio_entry,  NULL, NULL, NULL,  7, 0, 0);
K_THREAD_DEFINE(high_prio_thread, 1024, high_prio_entry, NULL, NULL, NULL,  4, 0, 0);

int main(void)
{
	k_sleep(K_FOREVER);
	return 0;
}
