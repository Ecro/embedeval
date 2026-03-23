#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/sensor.h>
#include <zephyr/drivers/i2c.h>
#include <zephyr/logging/log.h>

LOG_MODULE_REGISTER(my_sensor, LOG_LEVEL_DBG);

#define MY_SENSOR_WHO_AM_I_REG  0x0F
#define MY_SENSOR_WHO_AM_I_VAL  0x33
#define MY_SENSOR_DATA_REG      0x28

struct my_sensor_config {
	const struct device *i2c_dev;
	uint16_t i2c_addr;
};

struct my_sensor_data {
	int32_t last_sample;
};

static int my_sensor_init(const struct device *dev)
{
	const struct my_sensor_config *cfg = dev->config;
	uint8_t who_am_i;
	int ret;

	ret = i2c_reg_read_byte(cfg->i2c_dev, cfg->i2c_addr,
				MY_SENSOR_WHO_AM_I_REG, &who_am_i);
	if (ret < 0) {
		LOG_ERR("WHO_AM_I read failed: %d", ret);
		return ret;
	}

	if (who_am_i != MY_SENSOR_WHO_AM_I_VAL) {
		LOG_ERR("WHO_AM_I mismatch: got 0x%02x, expected 0x%02x",
			who_am_i, MY_SENSOR_WHO_AM_I_VAL);
		return -ENODEV;
	}

	printk("my_sensor: WHO_AM_I OK\n");
	return 0;
}

static int my_sensor_sample_fetch(const struct device *dev,
				   enum sensor_channel chan)
{
	const struct my_sensor_config *cfg = dev->config;
	struct my_sensor_data *data = dev->data;
	uint8_t raw;
	int ret;

	ret = i2c_reg_read_byte(cfg->i2c_dev, cfg->i2c_addr,
				MY_SENSOR_DATA_REG, &raw);
	if (ret < 0) {
		LOG_ERR("Data register read failed: %d", ret);
		return ret;
	}

	data->last_sample = (int32_t)raw;
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

static const struct my_sensor_config my_sensor_cfg_0 = {
	.i2c_dev  = DEVICE_DT_GET(DT_INST_BUS(0)),
	.i2c_addr = DT_INST_REG_ADDR(0),
};

SENSOR_DEVICE_DT_INST_DEFINE(0,
			      my_sensor_init,
			      NULL,
			      &my_sensor_data_0,
			      &my_sensor_cfg_0,
			      POST_KERNEL,
			      CONFIG_SENSOR_INIT_PRIORITY,
			      &my_sensor_api);
