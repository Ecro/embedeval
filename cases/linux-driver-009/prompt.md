Write a Linux kernel platform driver that controls a GPIO using the modern gpiod API.

Requirements:
1. Include linux/module.h, linux/platform_device.h, linux/gpio/consumer.h
2. Define MODULE_LICENSE("GPL"), MODULE_AUTHOR, MODULE_DESCRIPTION
3. Implement a platform_driver with probe and remove functions
4. In probe():
   - Request a GPIO using devm_gpiod_get() with GPIOD_OUT_LOW initial state
   - Store the gpio_desc pointer
   - Set GPIO direction to output using gpiod_direction_output()
   - Toggle the GPIO: set high with gpiod_set_value(), then log the state
   - Read back the GPIO value using gpiod_get_value()
   - Return error code from devm_gpiod_get if GPIO not available
5. In remove():
   - No manual GPIO release needed (devm_ handles it automatically)
   - Log that driver was removed
6. Register/unregister platform_driver in module_init/module_exit

CRITICAL: Use the modern gpiod API (gpiod_*):
- devm_gpiod_get() NOT gpio_request()
- gpiod_set_value() NOT gpio_set_value()
- gpiod_get_value() NOT gpio_get_value()
- gpiod_direction_output() NOT gpio_direction_output() with a number

The legacy gpio_request()/gpio_set_value() API is deprecated. Do NOT use it.
The devm_ prefix ensures automatic cleanup when the driver is removed.

Output ONLY the complete C source file.
