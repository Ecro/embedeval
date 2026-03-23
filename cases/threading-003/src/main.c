#include <zephyr/kernel.h>

K_SEM_DEFINE(event_sem, 0, 1);

void producer_entry(void *p1, void *p2, void *p3)
{
	for (int i = 0; i < 5; i++) {
		k_sleep(K_MSEC(200));
		k_sem_give(&event_sem);
		printk("Producer: event signaled\n");
	}
}

void consumer_entry(void *p1, void *p2, void *p3)
{
	for (int i = 0; i < 5; i++) {
		k_sem_take(&event_sem, K_FOREVER);
		printk("Consumer: event received\n");
	}
}

K_THREAD_DEFINE(producer, 1024, producer_entry, NULL, NULL, NULL, 5, 0, 0);
K_THREAD_DEFINE(consumer, 1024, consumer_entry, NULL, NULL, NULL, 6, 0, 0);

int main(void)
{
	k_sleep(K_FOREVER);
	return 0;
}
