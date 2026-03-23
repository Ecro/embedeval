Write a Zephyr RTOS application that configures two watchdog channels with different timeouts and feeds each at the correct rate.

Requirements:
1. Get the watchdog device using DEVICE_DT_GET(DT_ALIAS(watchdog0)) or equivalent
2. Check that the device is ready using device_is_ready()
3. Install channel 0 with a 1000ms timeout window (window.max = 1000), WDT_FLAG_RESET_SOC, no callback
4. Install channel 1 with a 5000ms timeout window (window.max = 5000), WDT_FLAG_RESET_SOC, no callback
5. Store the two channel IDs separately as ch0_id and ch1_id
6. Set up the watchdog using wdt_setup() with WDT_OPT_PAUSE_HALTED_BY_DBG
7. In the main loop, every 500ms feed channel 0 using its channel ID; every 4 seconds feed channel 1 using its channel ID
8. Print which channel is being fed each time

Use the Zephyr Watchdog API: wdt_install_timeout, wdt_setup, wdt_feed.

Include proper headers: zephyr/kernel.h, zephyr/drivers/watchdog.h, zephyr/device.h.

Output ONLY the complete C source file.
