#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/sensor.h>

#define FIFO_MAX_DEPTH  32

struct sensor_sample {
	struct sensor_value x;
	struct sensor_value y;
	struct sensor_value z;
};

static int read_fifo_watermark(const struct device *dev, int32_t *count)
{
	struct sensor_value attr;
	int ret;

	ret = sensor_attr_get(dev, SENSOR_CHAN_ACCEL_XYZ,
			      SENSOR_ATTR_FIFO_WATERMARK, &attr);
	if (ret < 0) {
		printk("sensor_attr_get (watermark) failed: %d\n", ret);
		return ret;
	}

	*count = attr.val1;
	return 0;
}

static int burst_read_fifo(const struct device *dev,
			    struct sensor_sample *buf, int32_t count)
{
	int ret;

	if (count <= 0 || count > FIFO_MAX_DEPTH) {
		printk("Invalid FIFO count %d (max %d)\n", count, FIFO_MAX_DEPTH);
		return -EINVAL;
	}

	for (int32_t i = 0; i < count; i++) {
		ret = sensor_sample_fetch(dev);
		if (ret < 0) {
			printk("sensor_sample_fetch failed at index %d: %d\n", i, ret);
			return ret;
		}

		ret = sensor_channel_get(dev, SENSOR_CHAN_ACCEL_X, &buf[i].x);
		if (ret < 0) {
			return ret;
		}

		ret = sensor_channel_get(dev, SENSOR_CHAN_ACCEL_Y, &buf[i].y);
		if (ret < 0) {
			return ret;
		}

		ret = sensor_channel_get(dev, SENSOR_CHAN_ACCEL_Z, &buf[i].z);
		if (ret < 0) {
			return ret;
		}
	}

	return 0;
}

int main(void)
{
	const struct device *dev = DEVICE_DT_GET(DT_ALIAS(sensor0));
	struct sensor_sample samples[FIFO_MAX_DEPTH];
	int32_t count = 0;
	int ret;

	if (!device_is_ready(dev)) {
		printk("Sensor device not ready\n");
		return -ENODEV;
	}

	ret = read_fifo_watermark(dev, &count);
	if (ret < 0) {
		printk("Failed to read FIFO watermark: %d\n", ret);
		return ret;
	}

	printk("FIFO watermark: %d samples\n", count);

	ret = burst_read_fifo(dev, samples, count);
	if (ret < 0) {
		printk("Burst FIFO read failed: %d\n", ret);
		return ret;
	}

	printk("First sample: x=%d.%06d y=%d.%06d z=%d.%06d\n",
	       samples[0].x.val1, samples[0].x.val2,
	       samples[0].y.val1, samples[0].y.val2,
	       samples[0].z.val1, samples[0].z.val2);

	k_sleep(K_FOREVER);
	return 0;
}
