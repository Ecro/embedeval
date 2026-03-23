Implement a Zephyr RTOS application that transfers data from an ISR to a thread using k_msgq (Zephyr message queue).

Requirements:
1. Include zephyr/kernel.h
2. Define a message struct with at least one uint32_t field (e.g. sensor_val)
3. Define a message queue with K_MSGQ_DEFINE for that struct type, with at least 8 slots
4. Implement an ISR function (isr_handler) that:
   - Puts one message into the queue using k_msgq_put with K_NO_WAIT (never K_FOREVER in ISR)
   - Does NOT call k_malloc, printk, or any blocking API
5. Implement a consumer thread function that:
   - Loops forever getting messages from the queue with k_msgq_get using K_FOREVER
   - Prints each received value with printk
6. Define the consumer thread with K_THREAD_DEFINE and a stack of at least 1024 bytes
7. In main(), simulate ISR firing by calling isr_handler() directly at least 3 times
8. Call k_sleep(K_MSEC(100)) in main after the simulated ISRs to allow thread to run

Output ONLY the complete C source file.
