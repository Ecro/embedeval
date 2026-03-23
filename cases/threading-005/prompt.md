Write a Zephyr RTOS application using a custom work queue with delayed work item submission.

Requirements:
1. Include zephyr/kernel.h
2. Define a custom work queue stack using K_THREAD_STACK_DEFINE with size 2048
3. Declare a struct k_work_q for the custom work queue
4. Declare a struct k_work_delayable for the delayed work item
5. Implement a work handler function that:
   - Prints "Work handler executed" using printk
   - Re-schedules itself on the custom work queue with a 500ms delay using k_work_schedule_for_queue()
6. In main():
   - Initialize the custom work queue with k_work_queue_start(), using the defined stack, stack size (K_THREAD_STACK_SIZEOF), priority 5, and NULL config
   - Initialize the delayable work item with k_work_init_delayable()
   - Schedule the first execution with k_work_schedule_for_queue() with a 100ms initial delay
   - Print "Work queue started" using printk
   - Sleep forever with k_sleep(K_FOREVER)

The work handler MUST NOT block (no k_sleep inside the handler).
The stack size MUST be at least 2048 bytes (work queue stacks need more space than thread stacks).
Use k_work_schedule_for_queue() to submit to the CUSTOM queue, not the system work queue.

Use the Zephyr API: K_THREAD_STACK_DEFINE, k_work_queue_start, k_work_delayable, k_work_init_delayable, k_work_schedule_for_queue.

Output ONLY the complete C source file.
