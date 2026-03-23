#include <zephyr/kernel.h>

K_THREAD_STACK_DEFINE(my_wq_stack, 2048);

static struct k_work_q my_work_q;
static struct k_work_delayable my_dwork;

static void work_handler(struct k_work *work)
{
	printk("Work handler executed\n");
	k_work_schedule_for_queue(&my_work_q, &my_dwork, K_MSEC(500));
}

int main(void)
{
	k_work_queue_start(&my_work_q, my_wq_stack,
			   K_THREAD_STACK_SIZEOF(my_wq_stack),
			   5, NULL);

	k_work_init_delayable(&my_dwork, work_handler);
	k_work_schedule_for_queue(&my_work_q, &my_dwork, K_MSEC(100));

	printk("Work queue started\n");
	k_sleep(K_FOREVER);
	return 0;
}
