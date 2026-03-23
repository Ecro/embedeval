Write a Zephyr RTOS application that configures a GPIO button interrupt to toggle an LED.

Requirements:
1. Get the LED device from devicetree alias "led0"
2. Get the button device from devicetree alias "sw0"
3. Configure the LED pin as output (initially off)
4. Configure the button pin as input with internal pull-up
5. Set up a GPIO interrupt callback on the button (edge-triggered, both edges or falling)
6. In the callback, toggle the LED state
7. In main(), after setup, sleep forever using k_sleep(K_FOREVER)

Use the Zephyr GPIO API (gpio_pin_configure_dt, gpio_pin_interrupt_configure_dt, gpio_init_callback, gpio_add_callback_dt, gpio_pin_toggle_dt).

Include proper headers: zephyr/kernel.h and zephyr/drivers/gpio.h.

Output ONLY the complete C source file.
