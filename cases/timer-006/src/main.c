#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/counter.h>

static volatile uint32_t alarm_ticks;

static void alarm_callback(const struct device *dev, uint8_t chan_id,
			    uint32_t ticks, void *user_data)
{
	/* ISR: non-blocking — only record value */
	counter_get_value(dev, (uint32_t *)&alarm_ticks);
}

int main(void)
{
	const struct device *counter = DEVICE_DT_GET(DT_ALIAS(counter0));

	if (!device_is_ready(counter)) {
		printk("Counter device not ready\n");
		return -1;
	}

	counter_start(counter);

	uint32_t initial_ticks = 0;

	counter_get_value(counter, &initial_ticks);

	struct counter_alarm_cfg alarm_cfg = {
		.callback = alarm_callback,
		.ticks = initial_ticks + 1000,
		.user_data = NULL,
		.flags = 0,
	};

	counter_set_channel_alarm(counter, 0, &alarm_cfg);

	k_sleep(K_MSEC(100));

	uint32_t final_ticks = 0;

	counter_get_value(counter, &final_ticks);

	uint32_t elapsed = final_ticks - initial_ticks;

	printk("Elapsed ticks: %u\n", elapsed);

	counter_stop(counter);
	return 0;
}
