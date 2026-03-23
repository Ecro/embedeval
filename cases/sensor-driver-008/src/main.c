#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/sensor.h>
#include <math.h>

static int fetch_accel(const struct device *dev,
		       struct sensor_value *ax,
		       struct sensor_value *ay,
		       struct sensor_value *az)
{
	int ret;

	ret = sensor_sample_fetch(dev);
	if (ret < 0) {
		printk("Accel fetch failed: %d\n", ret);
		return ret;
	}

	ret = sensor_channel_get(dev, SENSOR_CHAN_ACCEL_X, ax);
	if (ret < 0) {
		return ret;
	}

	ret = sensor_channel_get(dev, SENSOR_CHAN_ACCEL_Y, ay);
	if (ret < 0) {
		return ret;
	}

	ret = sensor_channel_get(dev, SENSOR_CHAN_ACCEL_Z, az);
	if (ret < 0) {
		return ret;
	}

	return 0;
}

static int fetch_gyro(const struct device *dev,
		      struct sensor_value *gx,
		      struct sensor_value *gy,
		      struct sensor_value *gz)
{
	int ret;

	ret = sensor_sample_fetch(dev);
	if (ret < 0) {
		printk("Gyro fetch failed: %d\n", ret);
		return ret;
	}

	ret = sensor_channel_get(dev, SENSOR_CHAN_GYRO_X, gx);
	if (ret < 0) {
		return ret;
	}

	ret = sensor_channel_get(dev, SENSOR_CHAN_GYRO_Y, gy);
	if (ret < 0) {
		return ret;
	}

	ret = sensor_channel_get(dev, SENSOR_CHAN_GYRO_Z, gz);
	if (ret < 0) {
		return ret;
	}

	return 0;
}

static void compute_orientation(struct sensor_value *ax,
				struct sensor_value *ay,
				struct sensor_value *az,
				float *pitch, float *roll)
{
	float ax_f = (float)sensor_value_to_double(ax);
	float ay_f = (float)sensor_value_to_double(ay);
	float az_f = (float)sensor_value_to_double(az);

	*pitch = atan2f(ax_f, sqrtf(ay_f * ay_f + az_f * az_f)) * 180.0f / 3.14159f;
	*roll  = atan2f(ay_f, az_f) * 180.0f / 3.14159f;
}

int main(void)
{
	const struct device *accel = DEVICE_DT_GET(DT_ALIAS(accel0));
	const struct device *gyro  = DEVICE_DT_GET(DT_ALIAS(gyro0));
	struct sensor_value ax, ay, az;
	struct sensor_value gx, gy, gz;
	float pitch = 0.0f;
	float roll  = 0.0f;
	int ret;

	if (!device_is_ready(accel)) {
		printk("Accelerometer not ready\n");
		return -ENODEV;
	}

	if (!device_is_ready(gyro)) {
		printk("Gyroscope not ready\n");
		return -ENODEV;
	}

	while (1) {
		ret = fetch_accel(accel, &ax, &ay, &az);
		if (ret < 0) {
			printk("Accel read error: %d\n", ret);
			k_sleep(K_MSEC(100));
			continue;
		}

		ret = fetch_gyro(gyro, &gx, &gy, &gz);
		if (ret < 0) {
			printk("Gyro read error: %d\n", ret);
			k_sleep(K_MSEC(100));
			continue;
		}

		compute_orientation(&ax, &ay, &az, &pitch, &roll);

		printk("Pitch: %.2f deg  Roll: %.2f deg\n",
		       (double)pitch, (double)roll);
		printk("Gyro: x=%d.%06d y=%d.%06d z=%d.%06d rad/s\n",
		       gx.val1, gx.val2, gy.val1, gy.val2, gz.val1, gz.val2);

		k_sleep(K_MSEC(100));
	}

	return 0;
}
