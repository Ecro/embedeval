#include <zephyr/kernel.h>
#include <zephyr/app_memory/app_memdomain.h>

K_APPMEM_PARTITION_DEFINE(app_partition);

static struct k_mem_domain app_domain;

K_APP_DMEM(app_partition) int shared_counter = 0;

K_THREAD_STACK_DEFINE(user_stack, 1024);
static struct k_thread user_thread;

static void user_thread_fn(void *p1, void *p2, void *p3)
{
	ARG_UNUSED(p1);
	ARG_UNUSED(p2);
	ARG_UNUSED(p3);

	for (int i = 0; i < 3; i++) {
		shared_counter++;
		printk("user_thread: shared_counter = %d\n", shared_counter);
		k_sleep(K_MSEC(100));
	}
}

int main(void)
{
	struct k_mem_partition *parts[] = { &app_partition };

	k_mem_domain_init(&app_domain, ARRAY_SIZE(parts), parts);

	k_thread_create(&user_thread, user_stack,
			K_THREAD_STACK_SIZEOF(user_stack),
			user_thread_fn, NULL, NULL, NULL,
			5, K_USER, K_NO_WAIT);

	k_mem_domain_add_thread(&app_domain, &user_thread);

	k_thread_join(&user_thread, K_FOREVER);
	printk("main: user thread finished, counter=%d\n", shared_counter);

	return 0;
}
