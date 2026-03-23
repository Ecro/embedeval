Write a Zephyr RTOS application that starts a watchdog and feeds it correctly, demonstrating that the watchdog is never disabled once started.

Requirements:
1. Get the watchdog device using DEVICE_DT_GET(DT_ALIAS(watchdog0)) and verify with device_is_ready()
2. Configure the watchdog with wdt_install_timeout():
   - flags = WDT_FLAG_RESET_SOC
   - window.min = 0, window.max = 2000
   - callback = NULL
3. Start the watchdog with wdt_setup() using WDT_OPT_PAUSE_HALTED_BY_DBG only
4. In the main loop, feed the watchdog every 1 second with wdt_feed() and print a heartbeat
5. Run for 10 iterations then exit

CRITICAL SAFETY RULE: Do NOT call wdt_disable() anywhere in the code. Once a watchdog is started in a production embedded system, it must never be disabled. Only WDT_OPT_PAUSE_HALTED_BY_DBG is an acceptable option for development pausing.

Include headers: zephyr/kernel.h, zephyr/device.h, zephyr/drivers/watchdog.h.

Output ONLY the complete C source file.
