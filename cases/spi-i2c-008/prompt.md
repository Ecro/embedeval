Write a Zephyr RTOS application that configures the device as an I2C target (slave) and responds to a controller.

Requirements:
1. Get the I2C bus device using DEVICE_DT_GET(DT_NODELABEL(i2c0))
2. Check device readiness with device_is_ready()
3. Define target address as 0x55
4. Implement all four required i2c_target_callbacks:
   - write_requested: called when controller initiates a write; return 0 to ACK
   - read_requested: called when controller initiates a read; set *val to first byte to send (e.g. 0xAB)
   - write_received: called for each byte written by controller; store the byte
   - read_processed: called after each byte sent; set *val for next byte (e.g. increment)
5. Define a struct i2c_target_config with the address and callbacks
6. Call i2c_target_register() to register the target config — do NOT use the deprecated i2c_slave_register()
7. Print "I2C target registered" after successful registration
8. Enter a k_sleep(K_FOREVER) loop to keep running

Use the Zephyr I2C target API: i2c_target_register, struct i2c_target_config, struct i2c_target_callbacks.

Include proper headers: zephyr/kernel.h, zephyr/device.h, zephyr/drivers/i2c.h.

Output ONLY the complete C source file.
