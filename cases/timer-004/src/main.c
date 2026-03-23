#include <zephyr/kernel.h>

void delayed_work_handler(struct k_work *work)
{
	printk("Delayed work executed\n");
}

K_WORK_DELAYABLE_DEFINE(my_dwork, delayed_work_handler);

int main(void)
{
	k_work_schedule(&my_dwork, K_MSEC(500));

	k_sleep(K_SECONDS(2));
	printk("Main done\n");

	return 0;
}
