Write a Zephyr RTOS application that configures sensor attributes before reading sensor data.

Requirements:
1. Include zephyr/kernel.h, zephyr/device.h, zephyr/drivers/sensor.h
2. Get the sensor device using DEVICE_DT_GET(DT_NODELABEL(my_sensor))
3. Check device readiness with device_is_ready()
4. Before reading any data, configure two sensor attributes:
   a. Set sampling frequency to 100 Hz:
      - Declare struct sensor_value odr = { .val1 = 100, .val2 = 0 }
      - Call sensor_attr_set(dev, SENSOR_CHAN_ACCEL_XYZ, SENSOR_ATTR_SAMPLING_FREQUENCY, &odr)
      - Check return value; print error and return if it fails
   b. Set full-scale range to 4g:
      - Declare struct sensor_value fs = { .val1 = 4, .val2 = 0 }
      - Call sensor_attr_set(dev, SENSOR_CHAN_ACCEL_XYZ, SENSOR_ATTR_FULL_SCALE, &fs)
      - Check return value; print error and return if it fails
5. Print "Sensor configured: 100 Hz, 4g" after successful attribute setup
6. In a loop:
   a. Call sensor_sample_fetch(dev)
   b. Call sensor_channel_get(dev, SENSOR_CHAN_ACCEL_XYZ, &val)
   c. Print the reading
   d. Sleep 10 milliseconds

Common mistakes: reading data before setting attributes, using wrong SENSOR_ATTR enum names, not initializing sensor_value correctly for the attribute value.

Output ONLY the complete C source file.
