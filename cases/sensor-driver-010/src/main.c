#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/sensor.h>
#include <zephyr/fs/nvs.h>
#include <zephyr/storage/flash_map.h>

#define NVS_PARTITION_ID  FIXED_PARTITION_ID(storage_partition)
#define NVS_CAL_KEY       1U

struct sensor_cal {
	int32_t offset_x;
	int32_t offset_y;
	int32_t offset_z;
};

static int nvs_init_fs(struct nvs_fs *fs)
{
	fs->flash_device = FIXED_PARTITION_DEVICE(storage_partition);
	fs->offset       = FIXED_PARTITION_OFFSET(storage_partition);

	return nvs_mount(fs);
}

static int load_calibration(struct nvs_fs *fs, struct sensor_cal *cal)
{
	return nvs_read(fs, NVS_CAL_KEY, cal, sizeof(*cal));
}

static int save_calibration(struct nvs_fs *fs, const struct sensor_cal *cal)
{
	return nvs_write(fs, NVS_CAL_KEY, cal, sizeof(*cal));
}

static int apply_calibration(const struct device *dev,
			      const struct sensor_cal *cal)
{
	struct sensor_value offset;
	int ret;

	offset.val1 = cal->offset_x;
	offset.val2 = 0;
	ret = sensor_attr_set(dev, SENSOR_CHAN_ACCEL_X, SENSOR_ATTR_OFFSET, &offset);
	if (ret < 0) {
		printk("Failed to set X offset: %d\n", ret);
		return ret;
	}

	offset.val1 = cal->offset_y;
	ret = sensor_attr_set(dev, SENSOR_CHAN_ACCEL_Y, SENSOR_ATTR_OFFSET, &offset);
	if (ret < 0) {
		printk("Failed to set Y offset: %d\n", ret);
		return ret;
	}

	offset.val1 = cal->offset_z;
	ret = sensor_attr_set(dev, SENSOR_CHAN_ACCEL_Z, SENSOR_ATTR_OFFSET, &offset);
	if (ret < 0) {
		printk("Failed to set Z offset: %d\n", ret);
		return ret;
	}

	return 0;
}

int main(void)
{
	const struct device *dev = DEVICE_DT_GET(DT_ALIAS(sensor0));
	struct nvs_fs fs;
	struct sensor_cal cal = {0};
	struct sensor_value ax, ay, az;
	int ret;

	if (!device_is_ready(dev)) {
		printk("Sensor not ready\n");
		return -ENODEV;
	}

	/* Step 1: Mount NVS */
	ret = nvs_init_fs(&fs);
	if (ret < 0) {
		printk("NVS mount failed: %d\n", ret);
		return ret;
	}

	/* Step 2: Try to load stored calibration */
	ret = load_calibration(&fs, &cal);
	if (ret > 0) {
		printk("Loaded calibration from NVS: x=%d y=%d z=%d\n",
		       cal.offset_x, cal.offset_y, cal.offset_z);
		apply_calibration(dev, &cal);
	} else {
		printk("No stored calibration (first boot or NVS empty)\n");
	}

	/* Step 3: Read raw sensor data to derive calibration */
	ret = sensor_sample_fetch(dev);
	if (ret < 0) {
		printk("sensor_sample_fetch failed: %d\n", ret);
		return ret;
	}

	sensor_channel_get(dev, SENSOR_CHAN_ACCEL_X, &ax);
	sensor_channel_get(dev, SENSOR_CHAN_ACCEL_Y, &ay);
	sensor_channel_get(dev, SENSOR_CHAN_ACCEL_Z, &az);

	/* Derive offsets: expected 0g on X/Y, expected +1g on Z */
	cal.offset_x = -ax.val1;
	cal.offset_y = -ay.val1;
	cal.offset_z = 10 - az.val1; /* 10 m/s^2 ~ 1g */

	printk("New calibration: x=%d y=%d z=%d\n",
	       cal.offset_x, cal.offset_y, cal.offset_z);

	/* Step 4: Save calibration to NVS */
	ret = save_calibration(&fs, &cal);
	if (ret < 0) {
		printk("NVS write failed: %d\n", ret);
	}

	/* Step 5: Apply new calibration */
	apply_calibration(dev, &cal);

	/* Step 6: Take another reading with calibration applied */
	sensor_sample_fetch(dev);
	sensor_channel_get(dev, SENSOR_CHAN_ACCEL_X, &ax);
	sensor_channel_get(dev, SENSOR_CHAN_ACCEL_Y, &ay);
	sensor_channel_get(dev, SENSOR_CHAN_ACCEL_Z, &az);

	printk("Calibrated reading: x=%d.%06d y=%d.%06d z=%d.%06d m/s^2\n",
	       ax.val1, ax.val2, ay.val1, ay.val2, az.val1, az.val2);

	k_sleep(K_FOREVER);
	return 0;
}
