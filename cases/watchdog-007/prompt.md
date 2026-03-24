Write a Zephyr RTOS application that implements a multi-thread watchdog monitoring pattern.

Requirements:
1. Get the watchdog device using DEVICE_DT_GET(DT_ALIAS(watchdog0)) and configure it with a 5-second timeout (wdt_install_timeout, WDT_FLAG_RESET_SOC, window.max = 5000)
2. Call wdt_setup() with WDT_OPT_PAUSE_HALTED_BY_DBG
3. Define 3 global atomic health flags using atomic_t: thread0_healthy, thread1_healthy, thread2_healthy
4. Define 3 worker threads (using K_THREAD_DEFINE) that each:
   a. Perform some work (a printk and k_sleep(K_SECONDS(1)))
   b. Set their respective atomic flag to 1 using atomic_set()
5. Define a supervisor thread that:
   a. Checks all 3 flags every 2 seconds
   b. If all 3 flags are set, clears them (atomic_clear) and calls wdt_feed()
   c. If any flag is NOT set, does NOT feed the WDT (allows reset)
   d. Logs current flag state with printk
6. All health flags MUST use appropriate synchronization for shared flags (not plain int)

Include headers: zephyr/kernel.h, zephyr/device.h, zephyr/drivers/watchdog.h, zephyr/sys/atomic.h.

Output ONLY the complete C source file.
