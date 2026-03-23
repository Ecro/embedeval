#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/counter.h>

void alarm_callback(const struct device *dev, uint8_t chan_id,
		    uint32_t ticks, void *user_data)
{
	printk("Alarm fired\n");
}

int main(void)
{
	const struct device *const counter_dev = DEVICE_DT_GET(DT_ALIAS(counter0));

	if (!device_is_ready(counter_dev)) {
		printk("Counter device not ready\n");
		return -1;
	}

	counter_start(counter_dev);

	struct counter_alarm_cfg alarm_cfg = {
		.callback = alarm_callback,
		.ticks = counter_us_to_ticks(counter_dev, 1000000U),
		.user_data = NULL,
		.flags = 0,
	};

	int err = counter_set_channel_alarm(counter_dev, 0, &alarm_cfg);

	if (err != 0) {
		printk("Failed to set alarm: %d\n", err);
		return -1;
	}

	k_sleep(K_SECONDS(3));

	return 0;
}
