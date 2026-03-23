/*
 * Deadlock-free multi-mutex acquisition via consistent lock ordering.
 * Both threads always lock A then B — never B then A.
 */

#include <zephyr/kernel.h>

K_MUTEX_DEFINE(mutex_a);
K_MUTEX_DEFINE(mutex_b);

#define STACK_SIZE 1024
#define PRIORITY   5

static void thread_one(void *p1, void *p2, void *p3)
{
	ARG_UNUSED(p1);
	ARG_UNUSED(p2);
	ARG_UNUSED(p3);

	while (1) {
		/* Lock ORDER: A first, then B — consistent across all threads */
		k_mutex_lock(&mutex_a, K_FOREVER);
		k_mutex_lock(&mutex_b, K_FOREVER);

		printk("Thread one working\n");
		k_sleep(K_MSEC(10));

		/* Unlock in REVERSE order: B first, then A */
		k_mutex_unlock(&mutex_b);
		k_mutex_unlock(&mutex_a);

		k_sleep(K_MSEC(5));
	}
}

static void thread_two(void *p1, void *p2, void *p3)
{
	ARG_UNUSED(p1);
	ARG_UNUSED(p2);
	ARG_UNUSED(p3);

	while (1) {
		/* SAME lock order as thread_one — prevents deadlock */
		k_mutex_lock(&mutex_a, K_FOREVER);
		k_mutex_lock(&mutex_b, K_FOREVER);

		printk("Thread two working\n");
		k_sleep(K_MSEC(10));

		/* Unlock in reverse order */
		k_mutex_unlock(&mutex_b);
		k_mutex_unlock(&mutex_a);

		k_sleep(K_MSEC(5));
	}
}

K_THREAD_DEFINE(t1_tid, STACK_SIZE, thread_one, NULL, NULL, NULL, PRIORITY, 0, 0);
K_THREAD_DEFINE(t2_tid, STACK_SIZE, thread_two, NULL, NULL, NULL, PRIORITY, 0, 0);

int main(void)
{
	printk("Deadlock-free multi-mutex demo\n");
	k_sleep(K_FOREVER);
	return 0;
}
