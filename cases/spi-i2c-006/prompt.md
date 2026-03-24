Write a Zephyr RTOS application that reads data from a slow I2C sensor device that uses clock stretching.

Requirements:
1. Get the I2C bus device using DEVICE_DT_GET(DT_NODELABEL(i2c0))
2. Verify the device is initialized and ready before use
3. Define sensor I2C address as 0x48
4. Read 2 bytes from the sensor using i2c_read() with a timeout wrapped in a retry loop
5. Use k_timeout_t with K_MSEC(100) for timeout — do NOT call a non-existent i2c_set_timeout() function
6. If i2c_read() returns -ETIMEDOUT or negative value, print an error message and return the error code
7. If read succeeds, print the two raw bytes and return 0
8. The timeout must NOT be K_FOREVER — clock stretching devices can hang the bus indefinitely

Use the Zephyr I2C API: i2c_read, DEVICE_DT_GET, DT_NODELABEL.

Include proper headers: zephyr/kernel.h, zephyr/device.h, zephyr/drivers/i2c.h, errno.h.

Output ONLY the complete C source file.
