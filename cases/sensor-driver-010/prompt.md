Write a Zephyr RTOS application that reads sensor calibration offsets, stores them in NVS, and applies them on the next boot using sensor_attr_set.

Requirements:
1. Include zephyr/kernel.h, zephyr/device.h, zephyr/drivers/sensor.h, zephyr/fs/nvs.h, zephyr/storage/flash_map.h
2. Use DT_ALIAS(sensor0) / DEVICE_DT_GET for the sensor
3. Define NVS_PARTITION_ID as FIXED_PARTITION_ID(storage_partition)
4. Define NVS_CAL_KEY as 1U (NVS key for calibration data)
5. Define struct sensor_cal { int32_t offset_x; int32_t offset_y; int32_t offset_z; }
6. Implement static int nvs_init_fs(struct nvs_fs *fs):
   - Set fs->flash_device = FIXED_PARTITION_DEVICE(storage_partition)
   - Set fs->offset = FIXED_PARTITION_OFFSET(storage_partition)
   - Call nvs_mount(fs) and return the result
7. Implement static int load_calibration(struct nvs_fs *fs, struct sensor_cal *cal):
   - Call nvs_read(fs, NVS_CAL_KEY, cal, sizeof(*cal))
   - Return the number of bytes read (positive) or negative on error/not-found
8. Implement static int save_calibration(struct nvs_fs *fs, const struct sensor_cal *cal):
   - Call nvs_write(fs, NVS_CAL_KEY, cal, sizeof(*cal))
   - Return result
9. Implement static int apply_calibration(const struct device *dev, const struct sensor_cal *cal):
   - For offset_x: set SENSOR_CHAN_ACCEL_X with SENSOR_ATTR_OFFSET via sensor_attr_set
   - For offset_y: set SENSOR_CHAN_ACCEL_Y with SENSOR_ATTR_OFFSET
   - For offset_z: set SENSOR_CHAN_ACCEL_Z with SENSOR_ATTR_OFFSET
   - Return 0 or first error encountered
10. In main():
    a. Mount NVS
    b. Try to load calibration from NVS — if found (load returns > 0), apply it immediately
    c. Take a sensor reading to get raw data (sensor_sample_fetch + sensor_channel_get)
    d. Derive calibration offsets from the reading (e.g., expected zero-g minus measured)
    e. Save new calibration to NVS
    f. Apply new calibration with apply_calibration()
    g. Take another reading and print it

Critical rules:
- NVS read MUST happen at startup BEFORE any sensor read (for boot-persistent offsets)
- Calibration MUST be applied via sensor_attr_set with SENSOR_ATTR_OFFSET — not by post-processing values
- NVS write happens AFTER collecting calibration data, not before

Output ONLY the complete C source file.
