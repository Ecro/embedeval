Write a Zephyr RTOS application that reads all three acceleration axes from an accelerometer with a single fetch.

Requirements:
1. Include zephyr/kernel.h, zephyr/device.h, zephyr/drivers/sensor.h
2. Get the accelerometer device using DEVICE_DT_GET(DT_NODELABEL(accel_sensor))
3. Verify the sensor device is available before reading
4. In a loop:
   a. Call sensor_sample_fetch(dev) ONCE per iteration and check return value
   b. Read all three channels by calling sensor_channel_get() three times — for SENSOR_CHAN_ACCEL_X, SENSOR_CHAN_ACCEL_Y, and SENSOR_CHAN_ACCEL_Z — using a separate struct sensor_value for each axis
   c. Print all three values: "Accel X: %d.%06d  Y: %d.%06d  Z: %d.%06d"
   d. Sleep for 100 milliseconds
5. Handle errors from sensor_sample_fetch and sensor_channel_get with printk

The key requirement is calling sensor_sample_fetch() only once per measurement cycle, then reading all three channels from that single snapshot.

Common mistakes: calling sensor_sample_fetch three times (once per channel), using the wrong SENSOR_CHAN enum (e.g., SENSOR_CHAN_ACCEL_XYZ instead of individual axes), not storing all three values before printing.

Output ONLY the complete C source file.
