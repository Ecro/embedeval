Write a Zephyr RTOS application that configures a window watchdog with both minimum and maximum feed constraints.

Requirements:
1. Get the watchdog device using DEVICE_DT_GET(DT_ALIAS(watchdog0)) and verify the device is initialized and ready before use
2. Configure the WDT with wdt_install_timeout() using:
   - flags = WDT_FLAG_RESET_SOC
   - window.min = 500 (feed must NOT happen before 500ms)
   - window.max = 2000 (feed must happen before 2000ms — system resets after this)
   - callback = NULL
   - IMPORTANT: window.min (500) MUST be greater than 0 and less than window.max (2000)
3. Call wdt_setup() with WDT_OPT_PAUSE_HALTED_BY_DBG
4. In the main loop, first sleep 1 second (to pass the minimum window) then feed the watchdog
   - Sleep duration must be >= window.min and < window.max so feeding occurs within [500ms, 2000ms]
5. Print timing information before and after each feed with printk
6. Repeat in an infinite loop

The window constraint is: 500ms <= time_since_last_feed <= 2000ms.

Include headers: zephyr/kernel.h, zephyr/device.h, zephyr/drivers/watchdog.h.

Output ONLY the complete C source file.
