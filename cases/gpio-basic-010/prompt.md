Write a Zephyr RTOS application that configures a GPIO as a wakeup source and enters deep sleep.

Requirements:
1. Include headers: zephyr/kernel.h, zephyr/drivers/gpio.h, zephyr/pm/pm.h
2. Get the button device from devicetree alias "sw0" using GPIO_DT_SPEC_GET
3. Verify device is ready with gpio_is_ready_dt(); return -1 if not
4. Configure the button pin as GPIO_INPUT with GPIO_PULL_UP
5. Set up a GPIO interrupt callback on the button using GPIO_INT_EDGE_TO_ACTIVE; register with gpio_init_callback and gpio_add_callback_dt
6. In the callback, simply print a wake message with printk
7. Configure GPIO as a wakeup source by calling gpio_pin_interrupt_configure_dt before the sleep loop
8. Enter deep sleep using pm_state_force(0U, &(struct pm_state_info){PM_STATE_SOFT_OFF, 0, 0})
9. After returning from sleep (wake event), print a wake confirmation message

Do NOT use gpio_wakeup_enable() — that function does not exist in Zephyr.
Do NOT use deepsleep() — that function does not exist in Zephyr.
Do NOT use HAL_PWR_EnterSTANDBYMode() — that is STM32 HAL only.
GPIO must be configured and callback registered BEFORE calling pm_state_force().

Output ONLY the complete C source file.
