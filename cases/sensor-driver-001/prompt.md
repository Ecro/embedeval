Write a Zephyr RTOS application that reads temperature from a sensor using the Zephyr sensor API.

Requirements:
1. Include zephyr/kernel.h, zephyr/device.h, zephyr/drivers/sensor.h
2. Get the sensor device using DEVICE_DT_GET(DT_NODELABEL(temp_sensor)) or DT_ALIAS
3. Verify the device is initialized and ready before use
4. In a loop:
   a. Call sensor_sample_fetch() to trigger a measurement
   b. Check return value for errors
   c. Call sensor_channel_get() with SENSOR_CHAN_AMBIENT_TEMP
   d. Check return value for errors
   e. Print the temperature using sensor_value_to_double() or val1/val2 fields
   f. Sleep for 2 seconds
5. Use struct sensor_value for the temperature reading
6. Handle all errors with printk messages

Use the Zephyr Sensor API: sensor_sample_fetch, sensor_channel_get, struct sensor_value.

Output ONLY the complete C source file.
