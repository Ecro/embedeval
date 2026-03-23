#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/sensor.h>

int main(void)
{
	const struct device *const dev = DEVICE_DT_GET(DT_NODELABEL(temp_sensor));
	struct sensor_value temp;
	int ret;

	if (!device_is_ready(dev)) {
		printk("Sensor device not ready\n");
		return -ENODEV;
	}

	while (1) {
		ret = sensor_sample_fetch(dev);
		if (ret < 0) {
			printk("Sensor fetch failed: %d\n", ret);
			k_sleep(K_SECONDS(2));
			continue;
		}

		ret = sensor_channel_get(dev, SENSOR_CHAN_AMBIENT_TEMP, &temp);
		if (ret < 0) {
			printk("Channel get failed: %d\n", ret);
			k_sleep(K_SECONDS(2));
			continue;
		}

		printk("Temperature: %d.%06d C\n", temp.val1, temp.val2);
		k_sleep(K_SECONDS(2));
	}

	return 0;
}
