Write a Zephyr RTOS application that uses the task watchdog API to monitor the main thread.

Requirements:
1. Include header: zephyr/task_wdt/task_wdt.h (in addition to zephyr/kernel.h)
2. Initialize the task watchdog subsystem with task_wdt_init(NULL) before adding any channels
3. Add a task watchdog channel for the main thread using task_wdt_add():
   - period_ms = 2000 (2 second timeout)
   - callback = NULL (use default reset action)
   - user_data = NULL
   - Store the return value as int task_wdt_id; check that it is >= 0
4. In the main loop:
   a. Print a heartbeat message with printk
   b. Feed the task watchdog by calling task_wdt_feed(task_wdt_id)
   c. Sleep for 1 second with k_sleep(K_SECONDS(1))
5. Repeat forever

task_wdt_init MUST be called before task_wdt_add. Feed period (1s) must be less than channel period (2s).

Include headers: zephyr/kernel.h, zephyr/task_wdt/task_wdt.h.

Output ONLY the complete C source file.
