Write a Zephyr RTOS application that controls LED brightness by varying the PWM duty cycle.

Requirements:
1. Get the PWM LED device from devicetree using PWM_DT_SPEC_GET(DT_ALIAS(pwm_led0))
2. Verify the device is ready using pwm_is_ready_dt()
3. Use a fixed period of 20000000 nanoseconds (20 ms, stored as uint32_t or as a named constant)
4. Step the duty cycle from 0 up to the full period in increments of 2000000 ns, then back down to 0
5. Call pwm_set_dt() to apply each duty cycle step
6. The duty cycle must never exceed the period (enforce: duty <= period)
7. Sleep 50 ms between each step using k_sleep(K_MSEC(50))
8. Loop the fade cycle forever

Use the Zephyr PWM DT spec API (pwm_set_dt).

Include proper headers: zephyr/kernel.h and zephyr/drivers/pwm.h.

Output ONLY the complete C source file.
