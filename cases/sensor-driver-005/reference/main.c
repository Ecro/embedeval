#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/sensor.h>
#include <zephyr/logging/log.h>

LOG_MODULE_REGISTER(my_sensor, LOG_LEVEL_DBG);

struct my_sensor_data {
	int32_t last_sample;
};

static int my_sensor_init(const struct device *dev)
{
	printk("my_sensor: init\n");
	return 0;
}

static int my_sensor_sample_fetch(const struct device *dev,
				   enum sensor_channel chan)
{
	struct my_sensor_data *data = dev->data;

	data->last_sample = 42;
	return 0;
}

static int my_sensor_channel_get(const struct device *dev,
				  enum sensor_channel chan,
				  struct sensor_value *val)
{
	struct my_sensor_data *data = dev->data;

	if (chan == SENSOR_CHAN_AMBIENT_TEMP) {
		val->val1 = data->last_sample;
		val->val2 = 0;
		return 0;
	}

	return -ENOTSUP;
}

static const struct sensor_driver_api my_sensor_api = {
	.sample_fetch = my_sensor_sample_fetch,
	.channel_get  = my_sensor_channel_get,
};

static struct my_sensor_data my_sensor_data_0;

SENSOR_DEVICE_DT_INST_DEFINE(0,
			      my_sensor_init,
			      NULL,
			      &my_sensor_data_0,
			      NULL,
			      POST_KERNEL,
			      CONFIG_SENSOR_INIT_PRIORITY,
			      &my_sensor_api);
