#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/sensor.h>

int main(void)
{
	const struct device *const dev = DEVICE_DT_GET(DT_NODELABEL(accel_sensor));
	struct sensor_value accel_x, accel_y, accel_z;
	int ret;

	if (!device_is_ready(dev)) {
		printk("Accelerometer not ready\n");
		return -ENODEV;
	}

	while (1) {
		ret = sensor_sample_fetch(dev);
		if (ret < 0) {
			printk("sensor_sample_fetch failed: %d\n", ret);
			k_sleep(K_MSEC(100));
			continue;
		}

		ret = sensor_channel_get(dev, SENSOR_CHAN_ACCEL_X, &accel_x);
		if (ret < 0) {
			printk("channel_get ACCEL_X failed: %d\n", ret);
			k_sleep(K_MSEC(100));
			continue;
		}

		ret = sensor_channel_get(dev, SENSOR_CHAN_ACCEL_Y, &accel_y);
		if (ret < 0) {
			printk("channel_get ACCEL_Y failed: %d\n", ret);
			k_sleep(K_MSEC(100));
			continue;
		}

		ret = sensor_channel_get(dev, SENSOR_CHAN_ACCEL_Z, &accel_z);
		if (ret < 0) {
			printk("channel_get ACCEL_Z failed: %d\n", ret);
			k_sleep(K_MSEC(100));
			continue;
		}

		printk("Accel X: %d.%06d  Y: %d.%06d  Z: %d.%06d\n",
		       accel_x.val1, accel_x.val2,
		       accel_y.val1, accel_y.val2,
		       accel_z.val1, accel_z.val2);

		k_sleep(K_MSEC(100));
	}

	return 0;
}
