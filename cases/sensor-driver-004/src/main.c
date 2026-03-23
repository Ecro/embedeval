#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/sensor.h>

int main(void)
{
	const struct device *const dev = DEVICE_DT_GET(DT_NODELABEL(my_sensor));
	struct sensor_value odr = { .val1 = 100, .val2 = 0 };
	struct sensor_value fs  = { .val1 = 4,   .val2 = 0 };
	struct sensor_value val;
	int ret;

	if (!device_is_ready(dev)) {
		printk("Sensor device not ready\n");
		return -ENODEV;
	}

	ret = sensor_attr_set(dev, SENSOR_CHAN_ACCEL_XYZ,
			      SENSOR_ATTR_SAMPLING_FREQUENCY, &odr);
	if (ret < 0) {
		printk("Failed to set sampling frequency: %d\n", ret);
		return ret;
	}

	ret = sensor_attr_set(dev, SENSOR_CHAN_ACCEL_XYZ,
			      SENSOR_ATTR_FULL_SCALE, &fs);
	if (ret < 0) {
		printk("Failed to set full-scale range: %d\n", ret);
		return ret;
	}

	printk("Sensor configured: 100 Hz, 4g\n");

	while (1) {
		ret = sensor_sample_fetch(dev);
		if (ret < 0) {
			printk("sensor_sample_fetch failed: %d\n", ret);
			k_sleep(K_MSEC(10));
			continue;
		}

		ret = sensor_channel_get(dev, SENSOR_CHAN_ACCEL_XYZ, &val);
		if (ret < 0) {
			printk("sensor_channel_get failed: %d\n", ret);
			k_sleep(K_MSEC(10));
			continue;
		}

		printk("Accel: %d.%06d\n", val.val1, val.val2);
		k_sleep(K_MSEC(10));
	}

	return 0;
}
