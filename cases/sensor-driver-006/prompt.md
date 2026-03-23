Write a minimal custom Zephyr sensor driver that uses an I2C backend, reads a WHO_AM_I register during init, and implements the standard sensor API.

Requirements:
1. Include zephyr/kernel.h, zephyr/device.h, zephyr/drivers/sensor.h, zephyr/drivers/i2c.h, zephyr/logging/log.h
2. Define constants:
   - MY_SENSOR_WHO_AM_I_REG  0x0F
   - MY_SENSOR_WHO_AM_I_VAL  0x33
   - MY_SENSOR_DATA_REG      0x28
3. Define driver config and data structs:
   struct my_sensor_config { const struct device *i2c_dev; uint16_t i2c_addr; };
   struct my_sensor_data   { int32_t last_sample; };
4. Implement static int my_sensor_init(const struct device *dev):
   - Get config: const struct my_sensor_config *cfg = dev->config
   - Read WHO_AM_I register: i2c_reg_read_byte(cfg->i2c_dev, cfg->i2c_addr, MY_SENSOR_WHO_AM_I_REG, &who_am_i)
   - If who_am_i != MY_SENSOR_WHO_AM_I_VAL: print error and return -ENODEV
   - Print "my_sensor: WHO_AM_I OK" and return 0
5. Implement static int my_sensor_sample_fetch(const struct device *dev, enum sensor_channel chan):
   - Read data register via i2c_reg_read_byte into a uint8_t raw
   - Store: data->last_sample = (int32_t)raw
   - Return 0, or propagate i2c error
6. Implement static int my_sensor_channel_get(const struct device *dev, enum sensor_channel chan, struct sensor_value *val):
   - If chan == SENSOR_CHAN_AMBIENT_TEMP: set val->val1 = data->last_sample, val->val2 = 0, return 0
   - Otherwise return -ENOTSUP
7. Wire up: static const struct sensor_driver_api my_sensor_api = { .sample_fetch = ..., .channel_get = ... }
8. Register: SENSOR_DEVICE_DT_INST_DEFINE(0, my_sensor_init, NULL, &my_sensor_data_0, &my_sensor_cfg_0, POST_KERNEL, CONFIG_SENSOR_INIT_PRIORITY, &my_sensor_api)
9. Declare static instances: my_sensor_data_0 and my_sensor_cfg_0 (using DT_INST macros for i2c_dev and i2c_addr)

Common mistakes:
- Using sensor_register() which does not exist in Zephyr
- Wrong struct name for driver API (must be sensor_driver_api not sensor_api or driver_api)
- Not checking WHO_AM_I return value (silent init success with wrong device)

Output ONLY the complete C source file.
