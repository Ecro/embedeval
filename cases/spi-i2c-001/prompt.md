Write a Zephyr RTOS application that reads a WHO_AM_I register from an I2C sensor.

Requirements:
1. Get the I2C bus device from devicetree node DT_NODELABEL(i2c0)
2. Verify the device is initialized and ready before use
3. Define the sensor I2C address as 0x68 (7-bit address)
4. Define the WHO_AM_I register address as 0x75
5. Read one byte from the WHO_AM_I register using i2c_reg_read_byte()
6. Check the return value for errors
7. Print the register value using printk if successful
8. Print an error message if the read fails
9. Return 0 on success, negative error code on failure

Use the Zephyr I2C API: i2c_reg_read_byte, DEVICE_DT_GET, DT_NODELABEL.

Include proper headers: zephyr/kernel.h, zephyr/device.h, zephyr/drivers/i2c.h.

Output ONLY the complete C source file.
