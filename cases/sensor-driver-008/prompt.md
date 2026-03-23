Write a Zephyr RTOS application that performs sensor fusion by reading both an accelerometer and a gyroscope and computing a simple orientation estimate.

Requirements:
1. Include zephyr/kernel.h, zephyr/device.h, zephyr/drivers/sensor.h, math.h (for atan2f, sqrtf)
2. Use two separate devices:
   - const struct device *accel = DEVICE_DT_GET(DT_ALIAS(accel0))
   - const struct device *gyro  = DEVICE_DT_GET(DT_ALIAS(gyro0))
3. Implement static int fetch_accel(const struct device *dev, struct sensor_value *ax, struct sensor_value *ay, struct sensor_value *az):
   - Call sensor_sample_fetch(dev)
   - Call sensor_channel_get(dev, SENSOR_CHAN_ACCEL_X, ax)
   - Call sensor_channel_get(dev, SENSOR_CHAN_ACCEL_Y, ay)
   - Call sensor_channel_get(dev, SENSOR_CHAN_ACCEL_Z, az)
   - Return 0 or propagate error
4. Implement static int fetch_gyro(const struct device *dev, struct sensor_value *gx, struct sensor_value *gy, struct sensor_value *gz):
   - Call sensor_sample_fetch(dev)
   - Call sensor_channel_get(dev, SENSOR_CHAN_GYRO_X, gx)
   - Call sensor_channel_get(dev, SENSOR_CHAN_GYRO_Y, gy)
   - Call sensor_channel_get(dev, SENSOR_CHAN_GYRO_Z, gz)
   - Return 0 or propagate error
5. Implement static void compute_orientation(struct sensor_value *ax, struct sensor_value *ay, struct sensor_value *az, float *pitch, float *roll):
   - Convert sensor_value to float: float ax_f = sensor_value_to_double(ax)
   - Compute: *pitch = atan2f(ax_f, sqrtf(ay_f*ay_f + az_f*az_f)) * 180.0f / 3.14159f
   - Compute: *roll  = atan2f(ay_f, az_f) * 180.0f / 3.14159f
6. In main(): check both devices ready, call fetch_accel AND fetch_gyro, then compute_orientation, print pitch and roll

Critical rules:
- BOTH sensor_sample_fetch calls must happen (one for accel, one for gyro)
- Use SENSOR_CHAN_ACCEL_X/Y/Z for accel, SENSOR_CHAN_GYRO_X/Y/Z for gyro — not the same channels
- compute_orientation must be called AFTER both fetches complete
- Do NOT use IMU.readAcceleration() (Arduino), iio_channel_read() (Linux IIO) — Zephyr sensor API only

Output ONLY the complete C source file.
