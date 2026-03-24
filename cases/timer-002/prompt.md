Write a Zephyr RTOS application that uses a one-shot kernel timer to submit work to the system work queue.

Requirements:
1. Define a work item using k_work_init() and a worker function
2. The worker function prints "Work executed" using printk
3. Define a one-shot timer using K_TIMER_DEFINE with an expiry function
4. The expiry function submits the work item to the system work queue using k_work_submit()
5. In main(), start the timer for a single one-shot firing at 1 second (configure as one-shot with no periodic repeat)
6. After starting the timer, sleep for 3 seconds then print "Done" and return

Use the Zephyr kernel API: K_TIMER_DEFINE, k_timer_start, k_work_init, k_work_submit, K_MSEC.

Include proper header: zephyr/kernel.h.

Output ONLY the complete C source file.
