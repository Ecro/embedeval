Write a Zephyr RTOS application that blinks 4 LEDs in a sequential chaser pattern.

Requirements:
1. Get each LED device from devicetree aliases "led0", "led1", "led2", "led3" using GPIO_DT_SPEC_GET
2. Store them in an array of struct gpio_dt_spec
3. Verify every LED device is ready using gpio_is_ready_dt() — return -1 if any fails
4. Configure all 4 LED pins as output (GPIO_OUTPUT_INACTIVE) before the main loop
5. In the main loop, iterate through the 4 LEDs in order:
   a. Turn the current LED on with gpio_pin_set_dt(..., 1)
   b. Sleep 200 ms
   c. Turn the current LED off with gpio_pin_set_dt(..., 0)
6. After all 4 LEDs have blinked once, repeat from the first LED forever

Use the Zephyr GPIO API (gpio_pin_configure_dt, gpio_pin_set_dt).

Include proper headers: zephyr/kernel.h and zephyr/drivers/gpio.h.

Output ONLY the complete C source file.
