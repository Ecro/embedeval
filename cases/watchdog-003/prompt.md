Write a Zephyr RTOS application that installs a watchdog timeout with a warning callback that runs before system reset.

Requirements:
1. Get the watchdog device using DEVICE_DT_GET(DT_ALIAS(watchdog0)) or equivalent
2. Check that the device is ready using device_is_ready()
3. Define a watchdog callback function that prints "WDT timeout! Resetting..." using printk
4. Configure the watchdog timeout with a 2000ms window, WDT_FLAG_RESET_SOC, and the callback function
5. Install the timeout using wdt_install_timeout() and store the channel ID
6. Set up the watchdog using wdt_setup() with WDT_OPT_PAUSE_HALTED_BY_DBG
7. In the main loop, feed the watchdog every 1 second for 5 iterations, printing a heartbeat message
8. After the loop, print "Stopping feed - reset expected" and loop forever without feeding

Use the Zephyr Watchdog API: wdt_install_timeout, wdt_setup, wdt_feed.

Include proper headers: zephyr/kernel.h, zephyr/drivers/watchdog.h, zephyr/device.h.

Output ONLY the complete C source file.
