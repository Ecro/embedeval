Write a Zephyr RTOS application that implements a cascaded safety pattern: a kernel timer feeds the watchdog, so if the timer stops, the WDT resets the system.

Requirements:
1. Get the watchdog device using DEVICE_DT_GET(DT_ALIAS(watchdog0)) and verify the device is initialized and ready before use
2. Configure the WDT with a 3-second timeout window (window.min = 0, window.max = 3000) using wdt_install_timeout() with WDT_FLAG_RESET_SOC
3. Start the watchdog with wdt_setup() using WDT_OPT_PAUSE_HALTED_BY_DBG
4. Define a k_timer that fires every 1 second (period < WDT timeout = 3 seconds)
5. In the timer expiry callback, call wdt_feed() to feed the watchdog
6. Start the timer in main() with k_timer_start
7. In main(), after starting the timer, enter an infinite loop that prints a heartbeat message every 5 seconds using printk and k_sleep(K_SECONDS(5))

The timer period MUST be shorter than the WDT timeout. Do NOT feed the watchdog in the main loop directly — only in the timer callback.

Include headers: zephyr/kernel.h, zephyr/device.h, zephyr/drivers/watchdog.h.

Output ONLY the complete C source file.
