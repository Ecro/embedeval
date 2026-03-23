Write a Zephyr RTOS application that implements GPIO interrupt debouncing using a kernel timer.

Requirements:
1. Get the LED device from devicetree alias "led0" and the button from "sw0" using GPIO_DT_SPEC_GET
2. Configure the LED pin as GPIO_OUTPUT_INACTIVE
3. Configure the button pin as GPIO_INPUT with GPIO_PULL_UP
4. Set up a GPIO interrupt callback on the button (GPIO_INT_EDGE_BOTH)
5. In the GPIO interrupt callback, start (or restart) a k_timer with a 50ms one-shot delay — do NOT read GPIO state or toggle LED inside the ISR
6. Define a timer expiry callback that reads the stable button state with gpio_pin_get_dt() and toggles the LED only if the button is pressed
7. Define the timer with K_TIMER_DEFINE
8. In main(), verify devices are ready with gpio_is_ready_dt(), configure pins, register the callback with gpio_init_callback and gpio_add_callback_dt, then sleep forever with k_sleep(K_FOREVER)

Use only real Zephyr APIs. Do NOT use gpio_debounce() (it does not exist) or GPIO_INT_DEBOUNCE (not a valid Zephyr flag).
Do NOT use floating-point arithmetic anywhere in the file.

Include headers: zephyr/kernel.h, zephyr/drivers/gpio.h.

Output ONLY the complete C source file.
