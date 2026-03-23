Write a Zephyr RTOS application that reads 6 bytes of accelerometer data from an I2C sensor in a burst read.

Requirements:
1. Get the I2C bus device using DEVICE_DT_GET(DT_NODELABEL(i2c0))
2. Check device readiness with device_is_ready()
3. Define the accelerometer I2C address as 0x19
4. Define the starting register address as 0x28 (OUT_X_L register on LIS2DH)
5. Read 6 consecutive bytes (registers 0x28 through 0x2D) using i2c_burst_read()
6. Store the result in a uint8_t array of 6 bytes
7. Check the return value for errors; print error message and return on failure
8. Parse the 6 bytes into three 16-bit signed values: x, y, z axes (little-endian, low byte first)
9. Print each axis value using printk

Use the Zephyr I2C API: i2c_burst_read, DEVICE_DT_GET, DT_NODELABEL.

Include proper headers: zephyr/kernel.h, zephyr/device.h, zephyr/drivers/i2c.h.

Output ONLY the complete C source file.
