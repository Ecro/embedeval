#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/sensor.h>

static int set_sampling_freq(const struct device *dev, int32_t freq_hz)
{
	struct sensor_value val = {
		.val1 = freq_hz,
		.val2 = 0,
	};
	int ret;

	ret = sensor_attr_set(dev, SENSOR_CHAN_ALL,
			      SENSOR_ATTR_SAMPLING_FREQUENCY, &val);
	if (ret < 0) {
		printk("sensor_attr_set (freq=%d) failed: %d\n", freq_hz, ret);
	}

	return ret;
}

static int read_sensor(const struct device *dev, struct sensor_value *out)
{
	int ret;

	ret = sensor_sample_fetch(dev);
	if (ret < 0) {
		printk("sensor_sample_fetch failed: %d\n", ret);
		return ret;
	}

	ret = sensor_channel_get(dev, SENSOR_CHAN_AMBIENT_TEMP, out);
	if (ret < 0) {
		printk("sensor_channel_get failed: %d\n", ret);
		return ret;
	}

	return 0;
}

int main(void)
{
	const struct device *dev = DEVICE_DT_GET(DT_ALIAS(sensor0));
	struct sensor_value val;
	int ret;

	if (!device_is_ready(dev)) {
		printk("Sensor device not ready\n");
		return -ENODEV;
	}

	for (int i = 0; i < 5; i++) {
		/* Wake sensor: set normal sampling rate */
		ret = set_sampling_freq(dev, 10);
		if (ret < 0) {
			printk("Failed to set active mode: %d\n", ret);
		}

		k_sleep(K_MSEC(100));

		/* Read sensor */
		ret = read_sensor(dev, &val);
		if (ret == 0) {
			printk("Sample %d: temp = %d.%06d C\n",
			       i + 1, val.val1, val.val2);
		}

		/* Sleep sensor: set low-power mode (freq = 0) */
		ret = set_sampling_freq(dev, 0);
		if (ret < 0) {
			printk("Failed to set low-power mode: %d\n", ret);
		}

		k_sleep(K_MSEC(900));
	}

	printk("Sensor power management demo complete\n");
	k_sleep(K_FOREVER);
	return 0;
}
