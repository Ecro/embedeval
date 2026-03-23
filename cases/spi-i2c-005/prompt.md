Write a Zephyr RTOS application that scans the I2C bus and reports all responding devices.

Requirements:
1. Get the I2C bus device using DEVICE_DT_GET(DT_NODELABEL(i2c0))
2. Check device readiness with device_is_ready()
3. Scan only valid 7-bit I2C addresses: 0x08 through 0x77 inclusive
4. Do NOT scan reserved addresses: 0x00-0x07 (general call, reserved) and 0x78-0x7F (10-bit prefix)
5. For each address in the valid range, probe by calling i2c_write() with a NULL buffer and length 0
6. If i2c_write() returns 0, the device acknowledged; print "Found device at 0x%02x" with the address
7. If i2c_write() returns a negative value, no device at that address; continue scanning
8. After scanning all addresses, print the total count of found devices
9. Return 0 on completion

Use the Zephyr I2C API: i2c_write, DEVICE_DT_GET, DT_NODELABEL.

Include proper headers: zephyr/kernel.h, zephyr/device.h, zephyr/drivers/i2c.h.

Output ONLY the complete C source file.
