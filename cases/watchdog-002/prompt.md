Write a Zephyr RTOS application that uses the task watchdog API to monitor a thread.

Requirements:
1. Include zephyr/task_wdt/task_wdt.h along with zephyr/kernel.h
2. Define a worker thread stack and thread object (512 bytes stack, priority 5)
3. The worker thread function runs a loop: prints "Worker running", feeds the task watchdog using task_wdt_feed(), then sleeps 1 second
4. In main(), initialize the task watchdog using task_wdt_init() with NULL for the callback
5. After initializing, register the worker thread with task_wdt_add() using a 3000ms timeout and NULL callback and NULL user_data; store the returned channel ID
6. Start the worker thread using k_thread_create()
7. Sleep forever using k_sleep(K_FOREVER)

Use the Zephyr task watchdog API: task_wdt_init, task_wdt_add, task_wdt_feed.

Include proper headers: zephyr/kernel.h, zephyr/task_wdt/task_wdt.h.

Output ONLY the complete C source file.
