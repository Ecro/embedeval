Write a Zephyr RTOS application that configures and feeds a watchdog timer.

Requirements:
1. Get the watchdog device using DEVICE_DT_GET(DT_ALIAS(watchdog0)) or equivalent
2. Check that the device is ready using device_is_ready()
3. Configure a watchdog timeout of 2000ms using wdt_install_timeout()
4. Use WDT_FLAG_RESET_SOC as the reset action flag
5. Set up the watchdog with wdt_setup() using WDT_OPT_PAUSE_HALTED_BY_DBG
6. In the main loop, feed the watchdog every 1 second using wdt_feed()
7. Print a heartbeat message with printk on each feed

Use the Zephyr Watchdog API: wdt_install_timeout, wdt_setup, wdt_feed.

Include proper headers: zephyr/kernel.h, zephyr/drivers/watchdog.h, zephyr/device.h.

Output ONLY the complete C source file.
