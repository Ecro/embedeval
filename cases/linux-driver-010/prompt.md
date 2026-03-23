Write a Linux kernel module that demonstrates deferred work processing using a workqueue.

Requirements:
1. Include linux/module.h, linux/workqueue.h, linux/interrupt.h, linux/timer.h
2. Define MODULE_LICENSE("GPL"), MODULE_AUTHOR, MODULE_DESCRIPTION
3. Define a work structure embedded in a device context struct:
   struct my_dev {
       struct work_struct work;
       int event_count;
   };
4. Implement a work handler function:
   static void my_work_handler(struct work_struct *work)
   - Use container_of() to get the parent struct
   - Perform processing here (e.g., increment counter, print info)
   - This function runs in process context (can sleep if needed)
5. Use INIT_WORK() to initialize the work struct before scheduling
6. Implement a simulated trigger function (e.g., timer callback or init trigger)
   that calls schedule_work() to queue the work
7. In module_init:
   - Allocate/initialize the device context
   - Call INIT_WORK() to initialize the work struct
   - Schedule an initial work item to demonstrate the pattern
8. In module_exit:
   - Call cancel_work_sync() to ensure work is not running before cleanup
   - Free allocated memory

IMPORTANT:
- Heavy processing MUST be in the work handler, NOT in interrupt/timer context
- INIT_WORK() MUST be called before schedule_work()
- Do NOT use k_work_submit() — that is Zephyr RTOS API, not Linux

Output ONLY the complete C source file.
