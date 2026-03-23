#include <zephyr/kernel.h>
#include <string.h>
#include <stdint.h>

#define POOL_SIZE 8

struct my_obj {
	int id;
	uint8_t data[32];
	bool in_use;
};

/* Static pool — no heap allocation */
static struct my_obj pool[POOL_SIZE];

/* Free list tracking: index of next free slot (-1 = none) */
static int free_head = 0;
static int free_next[POOL_SIZE];
static bool pool_initialized;

static void pool_init(void)
{
	for (int i = 0; i < POOL_SIZE - 1; i++)
		free_next[i] = i + 1;
	free_next[POOL_SIZE - 1] = -1;
	free_head = 0;
	pool_initialized = true;
}

struct my_obj *pool_alloc(void)
{
	if (!pool_initialized)
		pool_init();

	if (free_head < 0)
		return NULL;

	int idx = free_head;
	free_head = free_next[idx];

	pool[idx].in_use = true;
	pool[idx].id = idx;
	memset(pool[idx].data, 0, sizeof(pool[idx].data));
	return &pool[idx];
}

void pool_free(struct my_obj *obj)
{
	if (!obj)
		return;

	/* Validate pointer is within pool bounds */
	if (obj < &pool[0] || obj >= &pool[POOL_SIZE])
		return;

	int idx = (int)(obj - pool);
	obj->in_use = false;
	free_next[idx] = free_head;
	free_head = idx;
}

int main(void)
{
	struct my_obj *objs[POOL_SIZE];
	struct my_obj *extra;

	pool_init();
	printk("Object pool demo\n");

	/* Allocate all objects */
	for (int i = 0; i < POOL_SIZE; i++) {
		objs[i] = pool_alloc();
		if (objs[i])
			printk("Allocated object %d at %p\n", i, objs[i]);
	}

	/* Pool should be exhausted */
	extra = pool_alloc();
	printk("Extra alloc (should be NULL): %p\n", extra);

	/* Free two objects */
	pool_free(objs[0]);
	pool_free(objs[3]);

	/* Re-allocate */
	objs[0] = pool_alloc();
	printk("Re-allocated after free: %p\n", objs[0]);

	return 0;
}
