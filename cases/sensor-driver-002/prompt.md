Write a Zephyr RTOS application that configures a sensor data-ready trigger and processes samples in a callback.

Requirements:
1. Include zephyr/kernel.h, zephyr/device.h, zephyr/drivers/sensor.h
2. Get the sensor device using DEVICE_DT_GET(DT_NODELABEL(my_sensor))
3. Check device readiness with device_is_ready() before any sensor operation
4. Implement a trigger callback function with the correct Zephyr signature:
   static void data_ready_handler(const struct device *dev, const struct sensor_trigger *trig)
5. Inside the callback:
   a. Call sensor_sample_fetch(dev) and check return value
   b. Call sensor_channel_get(dev, SENSOR_CHAN_AMBIENT_TEMP, &val) and check return value
   c. Print the temperature value
6. In main(), set up the trigger AFTER confirming device is ready:
   a. Declare struct sensor_trigger trig = { .type = SENSOR_TRIG_DATA_READY, .chan = SENSOR_CHAN_AMBIENT_TEMP }
   b. Call sensor_trigger_set(dev, &trig, data_ready_handler) and check return value
   c. Print "Trigger configured, waiting for data"
   d. Enter k_sleep(K_FOREVER)

Common mistakes: calling sensor_trigger_set before device_is_ready, using wrong trigger type enum, omitting the callback function, missing error check on sensor_trigger_set.

Output ONLY the complete C source file.
