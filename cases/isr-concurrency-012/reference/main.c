#include <zephyr/kernel.h>
#include <zephyr/irq_offload.h>
#include <zephyr/sys/printk.h>

#define NUM_FIRES 5

struct shared_data {
	uint32_t count;
	uint32_t last_value;
};

static struct shared_data shared;
static struct k_spinlock shared_lock;

static void isr_handler(const void *arg)
{
	ARG_UNUSED(arg);
	k_spinlock_key_t key = k_spin_lock(&shared_lock);

	shared.count++;
	shared.last_value = shared.count * 10U;

	k_spin_unlock(&shared_lock, key);
}

K_THREAD_STACK_DEFINE(worker_stack, 1024);
static struct k_thread worker;

static void worker_entry(void *p1, void *p2, void *p3)
{
	ARG_UNUSED(p1);
	ARG_UNUSED(p2);
	ARG_UNUSED(p3);

	while (true) {
		k_spinlock_key_t key = k_spin_lock(&shared_lock);
		uint32_t c = shared.count;
		uint32_t v = shared.last_value;
		k_spin_unlock(&shared_lock, key);

		if (c >= NUM_FIRES) {
			printk("final count=%u value=%u\n", c, v);
			return;
		}
		k_msleep(20);
	}
}

int main(void)
{
	k_thread_create(&worker, worker_stack,
			K_THREAD_STACK_SIZEOF(worker_stack),
			worker_entry, NULL, NULL, NULL,
			5, 0, K_MSEC(10));

	for (int i = 0; i < NUM_FIRES; i++) {
		irq_offload(isr_handler, NULL);
		k_msleep(30);
	}

	k_thread_join(&worker, K_FOREVER);
	return 0;
}
