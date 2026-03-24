Write a Zephyr RTOS application where the main thread monitors a worker thread's health via a shared flag and only feeds the watchdog if the worker is alive.

Requirements:
1. Define a global flag to indicate worker thread health status, initialized to 0
2. Get the watchdog device, check device_is_ready(), install a 3000ms timeout with WDT_FLAG_RESET_SOC, call wdt_setup()
3. Define a worker thread (512 byte stack, priority 5) that runs a loop: sets worker_alive = 1, prints "Worker alive", then sleeps 500ms
4. In main(), start the worker thread using k_thread_create()
5. In the main loop, every 1 second: check worker_alive, if it is 1 then reset worker_alive to 0 and call wdt_feed(); if it is 0 then print "Worker stalled! Not feeding WDT" and do NOT feed
6. Print "Feeding WDT" when feeding

Use the Zephyr Watchdog API and threading: wdt_install_timeout, wdt_setup, wdt_feed, k_thread_create.

Include proper headers: zephyr/kernel.h, zephyr/drivers/watchdog.h, zephyr/device.h.

Output ONLY the complete C source file.
