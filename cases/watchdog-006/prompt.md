Write a Zephyr RTOS application that configures a watchdog with a pre-timeout ISR callback that executes before the system resets.

Requirements:
1. Get the watchdog device using DEVICE_DT_GET(DT_ALIAS(watchdog0)) and verify with device_is_ready()
2. Define a watchdog callback function matching the signature:
   void wdt_callback(const struct device *dev, int channel_id)
3. The callback MUST be short and non-blocking:
   - Only call printk to log a warning message (e.g. "WDT pre-timeout! System will reset.\n")
   - Do NOT call k_sleep, wdt_feed, or any blocking function inside the callback
4. Configure the watchdog timeout using wdt_install_timeout() with:
   - flags = WDT_FLAG_RESET_SOC
   - window.min = 0, window.max = 2000 (2 second timeout)
   - callback = wdt_callback (set the pre-timeout callback)
5. Call wdt_setup() with WDT_OPT_PAUSE_HALTED_BY_DBG
6. In the main loop, feed the watchdog every 1 second normally, but stop feeding after 5 iterations to let the WDT expire and trigger the callback

Include headers: zephyr/kernel.h, zephyr/device.h, zephyr/drivers/watchdog.h.

Output ONLY the complete C source file.
