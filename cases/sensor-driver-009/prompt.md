Write a Zephyr RTOS application that puts a sensor into low-power mode between reads using the sensor attribute API.

Requirements:
1. Include zephyr/kernel.h, zephyr/device.h, zephyr/drivers/sensor.h
2. Use DT_ALIAS(sensor0) / DEVICE_DT_GET to get the sensor device
3. Implement static int set_sampling_freq(const struct device *dev, int32_t freq_hz):
   - Declare struct sensor_value val = { .val1 = freq_hz, .val2 = 0 }
   - Call sensor_attr_set(dev, SENSOR_CHAN_ALL, SENSOR_ATTR_SAMPLING_FREQUENCY, &val)
   - Return the result (0 on success, negative on error)
4. Implement static int read_sensor(const struct device *dev, struct sensor_value *out):
   - Call sensor_sample_fetch(dev) — return error if it fails
   - Call sensor_channel_get(dev, SENSOR_CHAN_AMBIENT_TEMP, out) — return error if it fails
   - Return 0
5. In main():
   - Check device is ready with device_is_ready()
   - Loop 5 times:
     a. Set normal sampling rate: set_sampling_freq(dev, 10) — 10 Hz active mode
     b. k_sleep(K_MSEC(100)) to let sensor stabilize
     c. Call read_sensor(dev, &val) and print the value
     d. Set low-power mode: set_sampling_freq(dev, 0) — 0 Hz = sensor idle/low-power
     e. k_sleep(K_MSEC(900)) — sleep between reads

Critical rules:
- Low-power mode (freq=0) must be set AFTER the read, not before
- Normal mode (freq>0) must be set BEFORE the read
- Use sensor_attr_set with SENSOR_ATTR_SAMPLING_FREQUENCY — not a custom ioctl or register write
- The attribute API must be used (not a direct register write via i2c/spi)

Output ONLY the complete C source file.
