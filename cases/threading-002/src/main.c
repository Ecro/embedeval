#include <zephyr/kernel.h>

K_MUTEX_DEFINE(counter_mutex);

static uint32_t shared_counter;

void thread_a_entry(void *p1, void *p2, void *p3)
{
	for (int i = 0; i < 5; i++) {
		k_mutex_lock(&counter_mutex, K_FOREVER);
		shared_counter++;
		printk("Thread A: counter=%u\n", shared_counter);
		k_mutex_unlock(&counter_mutex);
		k_sleep(K_MSEC(50));
	}
}

void thread_b_entry(void *p1, void *p2, void *p3)
{
	for (int i = 0; i < 5; i++) {
		k_mutex_lock(&counter_mutex, K_FOREVER);
		shared_counter++;
		printk("Thread B: counter=%u\n", shared_counter);
		k_mutex_unlock(&counter_mutex);
		k_sleep(K_MSEC(50));
	}
}

K_THREAD_DEFINE(thread_a, 1024, thread_a_entry, NULL, NULL, NULL, 5, 0, 0);
K_THREAD_DEFINE(thread_b, 1024, thread_b_entry, NULL, NULL, NULL, 6, 0, 0);

int main(void)
{
	k_sleep(K_MSEC(1500));
	printk("Final counter: %u\n", shared_counter);
	return 0;
}
