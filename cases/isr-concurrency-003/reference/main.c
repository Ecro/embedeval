/*
 * Spinlock-protected shared state between ISR and thread
 * k_spinlock is safe in ISR context; k_mutex is NOT
 */

#include <zephyr/kernel.h>

static struct k_spinlock counter_lock;
static uint32_t shared_counter;

/* Simulated ISR: uses spinlock (mutex forbidden in ISR) */
static void isr_handler(const void *arg)
{
	ARG_UNUSED(arg);
	k_spinlock_key_t key;

	key = k_spin_lock(&counter_lock);
	shared_counter++;
	k_spin_unlock(&counter_lock, key);
}

/* Reader thread: acquires spinlock to read safely */
static void reader_thread(void *p1, void *p2, void *p3)
{
	ARG_UNUSED(p1);
	ARG_UNUSED(p2);
	ARG_UNUSED(p3);

	for (int i = 0; i < 5; i++) {
		k_spinlock_key_t key;
		uint32_t val;

		key = k_spin_lock(&counter_lock);
		val = shared_counter;
		k_spin_unlock(&counter_lock, key);

		printk("counter=%u\n", val);
		k_sleep(K_MSEC(100));
	}
}

K_THREAD_DEFINE(reader_tid, 1024,
		reader_thread, NULL, NULL, NULL,
		5, 0, 0);

int main(void)
{
	/* Simulate ISR firing 5 times */
	isr_handler(NULL);
	isr_handler(NULL);
	isr_handler(NULL);
	isr_handler(NULL);
	isr_handler(NULL);

	/* Allow reader thread to observe counter */
	k_sleep(K_MSEC(600));

	return 0;
}
