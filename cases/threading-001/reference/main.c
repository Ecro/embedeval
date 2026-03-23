#include <zephyr/kernel.h>

struct data_item {
	uint32_t value;
};

K_MSGQ_DEFINE(my_msgq, sizeof(struct data_item), 10, 4);

void producer_entry(void *p1, void *p2, void *p3)
{
	struct data_item msg;
	uint32_t count = 0;

	while (1) {
		msg.value = count++;
		if (k_msgq_put(&my_msgq, &msg, K_NO_WAIT) == 0) {
			printk("Producer sent: %u\n", msg.value);
		}
		k_sleep(K_MSEC(100));
	}
}

void consumer_entry(void *p1, void *p2, void *p3)
{
	struct data_item msg;

	while (1) {
		if (k_msgq_get(&my_msgq, &msg, K_FOREVER) == 0) {
			printk("Consumer received: %u\n", msg.value);
		}
	}
}

K_THREAD_DEFINE(producer, 1024, producer_entry, NULL, NULL, NULL, 5, 0, 0);
K_THREAD_DEFINE(consumer, 1024, consumer_entry, NULL, NULL, NULL, 6, 0, 0);

int main(void)
{
	k_sleep(K_FOREVER);
	return 0;
}
