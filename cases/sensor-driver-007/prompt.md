Write a Zephyr RTOS application that reads sensor data using FIFO burst-read with watermark checking.

Requirements:
1. Include zephyr/kernel.h, zephyr/device.h, zephyr/drivers/sensor.h
2. Use DT_ALIAS(sensor0) / DEVICE_DT_GET to get the sensor device
3. Define:
   - FIFO_MAX_DEPTH 32  (maximum number of samples the FIFO can hold)
   - struct sensor_sample { struct sensor_value x, y, z; }
4. Implement static int read_fifo_watermark(const struct device *dev, int32_t *count):
   - Use sensor_attr_get(dev, SENSOR_CHAN_ACCEL_XYZ, SENSOR_ATTR_FIFO_WATERMARK, &attr)
   - Store the integer value: *count = attr.val1
   - Return 0 on success, propagate error on failure
5. Implement static int burst_read_fifo(const struct device *dev, struct sensor_sample *buf, int32_t count):
   - If count <= 0 or count > FIFO_MAX_DEPTH: print warning and return -EINVAL
   - Loop count times:
     - Call sensor_sample_fetch(dev) for each sample
     - Call sensor_channel_get(dev, SENSOR_CHAN_ACCEL_X, &buf[i].x)
     - Call sensor_channel_get(dev, SENSOR_CHAN_ACCEL_Y, &buf[i].y)
     - Call sensor_channel_get(dev, SENSOR_CHAN_ACCEL_Z, &buf[i].z)
     - On any error: print error index and return error
   - Return 0
6. In main():
   - Verify the device is initialized and ready before use
   - Call read_fifo_watermark() to get count
   - Declare struct sensor_sample samples[FIFO_MAX_DEPTH]
   - Call burst_read_fifo(dev, samples, count)
   - Print the first sample's x, y, z values

Safety rules:
- MUST check watermark BEFORE reading — do not read a fixed number of samples
- Buffer size MUST accommodate FIFO_MAX_DEPTH samples (no undersized buffers)
- count > FIFO_MAX_DEPTH must be guarded to prevent buffer overflow

Output ONLY the complete C source file.
