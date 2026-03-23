Write a Zephyr RTOS application that schedules a delayable work item to execute after a 500ms delay.

Requirements:
1. Define a delayable work item using K_WORK_DELAYABLE_DEFINE with a worker function
2. The worker function prints "Delayed work executed" using printk
3. In main(), schedule the work item with a 500ms delay using k_work_schedule()
4. Use K_MSEC(500) as the delay argument to k_work_schedule()
5. Sleep for 2 seconds to allow the work to execute, then print "Main done" and return

Use the Zephyr work queue API: K_WORK_DELAYABLE_DEFINE, k_work_schedule, K_MSEC.

Include proper header: zephyr/kernel.h.

Output ONLY the complete C source file.
