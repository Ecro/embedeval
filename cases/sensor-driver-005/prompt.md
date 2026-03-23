Write a minimal custom Zephyr sensor driver that registers itself via the Device Tree and implements the sensor API.

Requirements:
1. Include zephyr/kernel.h, zephyr/device.h, zephyr/drivers/sensor.h, zephyr/logging/log.h
2. Define a driver data struct:
   struct my_sensor_data { int32_t last_sample; };
3. Implement the device init function with the correct signature:
   static int my_sensor_init(const struct device *dev)
   - Print "my_sensor: init" and return 0
4. Implement sample_fetch with the correct signature:
   static int my_sensor_sample_fetch(const struct device *dev, enum sensor_channel chan)
   - Get data pointer with: struct my_sensor_data *data = dev->data
   - Simulate a reading: data->last_sample = 42
   - Return 0
5. Implement channel_get with the correct signature:
   static int my_sensor_channel_get(const struct device *dev, enum sensor_channel chan, struct sensor_value *val)
   - Get data pointer
   - If chan == SENSOR_CHAN_AMBIENT_TEMP: set val->val1 = data->last_sample, val->val2 = 0, return 0
   - Otherwise return -ENOTSUP
6. Define the driver API struct using sensor_driver_api:
   static const struct sensor_driver_api my_sensor_api = {
       .sample_fetch = my_sensor_sample_fetch,
       .channel_get  = my_sensor_channel_get,
   };
7. Register the driver using the macro:
   SENSOR_DEVICE_DT_INST_DEFINE(0, my_sensor_init, NULL, &my_sensor_data_0, NULL,
                                 POST_KERNEL, CONFIG_SENSOR_INIT_PRIORITY, &my_sensor_api);
8. Declare the per-instance data: static struct my_sensor_data my_sensor_data_0;

Common mistakes: wrong api struct type name (must be sensor_driver_api), missing sample_fetch in api struct, wrong device init signature, not using DT instance macros, getting data pointer with wrong cast.

Output ONLY the complete C source file.
