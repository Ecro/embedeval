Implement a Zephyr RTOS application that uses k_work for ISR-deferred processing. The ISR must do minimal work and submit a work item; the heavy processing happens in the work handler running in thread context.

Requirements:
1. Include zephyr/kernel.h
2. Declare a global struct k_work for the deferred processing
3. Declare a global atomic_t isr_event_count to track ISR firings
4. Implement a work handler function (work_handler) that:
   - Takes a struct k_work * parameter
   - Reads the isr_event_count
   - Performs the "heavy" processing (e.g. a loop with printk showing values)
   - Prints "work_handler: events=%d" with printk
5. Implement an ISR function (isr_handler) that:
   - Increments isr_event_count atomically with atomic_inc
   - Calls k_work_submit() to submit the work item
   - Does NOT do heavy processing directly
   - Does NOT call k_work_init() (init must happen before ISR fires, in main)
6. In main():
   - Call k_work_init(&my_work, work_handler) BEFORE simulating any ISR
   - Simulate ISR firing 3 times by calling isr_handler() directly
   - Call k_sleep(K_MSEC(200)) to allow work queue to drain

Output ONLY the complete C source file.
