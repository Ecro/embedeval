#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/sensor.h>

static void data_ready_handler(const struct device *dev,
				const struct sensor_trigger *trig)
{
	struct sensor_value val;
	int ret;

	ret = sensor_sample_fetch(dev);
	if (ret < 0) {
		printk("Trigger fetch failed: %d\n", ret);
		return;
	}

	ret = sensor_channel_get(dev, SENSOR_CHAN_AMBIENT_TEMP, &val);
	if (ret < 0) {
		printk("Trigger channel_get failed: %d\n", ret);
		return;
	}

	printk("Temperature (trigger): %d.%06d C\n", val.val1, val.val2);
}

int main(void)
{
	const struct device *const dev = DEVICE_DT_GET(DT_NODELABEL(my_sensor));
	struct sensor_trigger trig = {
		.type = SENSOR_TRIG_DATA_READY,
		.chan = SENSOR_CHAN_AMBIENT_TEMP,
	};
	int ret;

	if (!device_is_ready(dev)) {
		printk("Sensor device not ready\n");
		return -ENODEV;
	}

	ret = sensor_trigger_set(dev, &trig, data_ready_handler);
	if (ret < 0) {
		printk("sensor_trigger_set failed: %d\n", ret);
		return ret;
	}

	printk("Trigger configured, waiting for data\n");
	k_sleep(K_FOREVER);

	return 0;
}
