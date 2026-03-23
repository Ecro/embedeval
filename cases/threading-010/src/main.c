/*
 * Reader-Writer lock pattern for Zephyr RTOS.
 * Multiple concurrent readers; exclusive writer access.
 * Uses k_mutex for reader_count and k_sem for write exclusion.
 */

#include <zephyr/kernel.h>

/* Protects reader_count modifications */
K_MUTEX_DEFINE(write_mutex);

/* Binary semaphore: held by readers collectively; taken by writer */
static struct k_sem reader_sem;

static int reader_count;

static int shared_data;

static void rwlock_read_lock(void)
{
	k_mutex_lock(&write_mutex, K_FOREVER);
	reader_count++;
	if (reader_count == 1) {
		/* First reader blocks any waiting writer */
		k_sem_take(&reader_sem, K_FOREVER);
	}
	k_mutex_unlock(&write_mutex);
}

static void rwlock_read_unlock(void)
{
	k_mutex_lock(&write_mutex, K_FOREVER);
	reader_count--;
	if (reader_count == 0) {
		/* Last reader unblocks a waiting writer */
		k_sem_give(&reader_sem);
	}
	k_mutex_unlock(&write_mutex);
}

static void rwlock_write_lock(void)
{
	/* Writer takes the semaphore exclusively */
	k_sem_take(&reader_sem, K_FOREVER);
}

static void rwlock_write_unlock(void)
{
	k_sem_give(&reader_sem);
}

#define STACK_SIZE 1024

static void reader_thread(void *p1, void *p2, void *p3)
{
	ARG_UNUSED(p1);
	ARG_UNUSED(p2);
	ARG_UNUSED(p3);

	while (1) {
		rwlock_read_lock();

		printk("Reader: data=%d (active readers=%d)\n", shared_data, reader_count);
		k_sleep(K_MSEC(50));

		rwlock_read_unlock();

		k_sleep(K_MSEC(10));
	}
}

static void writer_thread(void *p1, void *p2, void *p3)
{
	ARG_UNUSED(p1);
	ARG_UNUSED(p2);
	ARG_UNUSED(p3);

	while (1) {
		k_sleep(K_MSEC(200));

		rwlock_write_lock();

		shared_data++;
		printk("Writer: updated data=%d\n", shared_data);

		rwlock_write_unlock();
	}
}

K_THREAD_DEFINE(r1_tid, STACK_SIZE, reader_thread, NULL, NULL, NULL, 7, 0, 0);
K_THREAD_DEFINE(r2_tid, STACK_SIZE, reader_thread, NULL, NULL, NULL, 7, 0, 0);
K_THREAD_DEFINE(w1_tid, STACK_SIZE, writer_thread, NULL, NULL, NULL, 6, 0, 0);

int main(void)
{
	/* reader_sem initial=1: writer can take it immediately when no readers */
	k_sem_init(&reader_sem, 1, 1);

	printk("Reader-writer lock demo started\n");
	k_sleep(K_FOREVER);
	return 0;
}
