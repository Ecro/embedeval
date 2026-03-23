/*
 * Thread-safe singleton initialization using double-check locking.
 * Fast path avoids locking on every call after first initialization.
 */

#include <zephyr/kernel.h>

K_MUTEX_DEFINE(init_mutex);

struct shared_resource {
	uint32_t value;
	bool     ready;
};

static struct shared_resource resource;
static bool initialized = false;

static struct shared_resource *get_resource(void)
{
	/* First check — fast path, no lock needed after init */
	if (initialized) {
		return &resource;
	}

	/* Acquire lock to serialize initialization */
	k_mutex_lock(&init_mutex, K_FOREVER);

	/* Second check under lock — another thread may have initialized while we waited */
	if (!initialized) {
		resource.value = 0xBEEF;
		resource.ready = true;
		initialized = true;
		printk("Resource initialized\n");
	}

	k_mutex_unlock(&init_mutex);

	return &resource;
}

#define STACK_SIZE 1024
#define PRIORITY   5

static void thread_one(void *p1, void *p2, void *p3)
{
	ARG_UNUSED(p1);
	ARG_UNUSED(p2);
	ARG_UNUSED(p3);

	struct shared_resource *r = get_resource();

	printk("Thread one: value=0x%08X ready=%d\n", r->value, r->ready);
}

static void thread_two(void *p1, void *p2, void *p3)
{
	ARG_UNUSED(p1);
	ARG_UNUSED(p2);
	ARG_UNUSED(p3);

	struct shared_resource *r = get_resource();

	printk("Thread two: value=0x%08X ready=%d\n", r->value, r->ready);
}

K_THREAD_DEFINE(t1_tid, STACK_SIZE, thread_one, NULL, NULL, NULL, PRIORITY,     0, 0);
K_THREAD_DEFINE(t2_tid, STACK_SIZE, thread_two, NULL, NULL, NULL, PRIORITY + 1, 0, 0);

int main(void)
{
	printk("Singleton demo started\n");
	k_sleep(K_FOREVER);
	return 0;
}
