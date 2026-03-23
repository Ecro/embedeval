Write a Zephyr RTOS application that writes a block of data to consecutive I2C registers using a repeated start condition.

Requirements:
1. Get the I2C bus device using DEVICE_DT_GET(DT_NODELABEL(i2c0))
2. Check device readiness with device_is_ready()
3. Define device I2C address as 0x3C
4. Write 4 bytes of configuration data to register 0x10 and following registers:
   - Prepare a buffer where byte 0 is the register address (0x10) and bytes 1-4 are data values
5. Use i2c_transfer() with an array of struct i2c_msg:
   - First message: write with the register address + data, flags = I2C_MSG_WRITE | I2C_MSG_RESTART
   - Second message: a zero-length read with flags = I2C_MSG_READ | I2C_MSG_STOP to terminate
   - OR use a single write message with I2C_MSG_WRITE | I2C_MSG_STOP containing register addr + data
6. The RESTART flag (I2C_MSG_RESTART) must be used — do NOT use a STOP then re-START sequence
7. If i2c_transfer() returns negative, print error and return the error code
8. Print "Register write OK" on success

Use the Zephyr I2C API: i2c_transfer, struct i2c_msg, I2C_MSG_WRITE, I2C_MSG_RESTART, I2C_MSG_STOP.

Include proper headers: zephyr/kernel.h, zephyr/device.h, zephyr/drivers/i2c.h.

Output ONLY the complete C source file.
