Write a Zephyr RTOS application implementing a producer-consumer pattern using a message queue.

Requirements:
1. Define a simple message struct with an uint32_t value field
2. Define a message queue using K_MSGQ_DEFINE that holds up to 10 messages
3. Create a producer thread using K_THREAD_DEFINE with stack size 1024 and priority 5
4. Create a consumer thread using K_THREAD_DEFINE with stack size 1024 and priority 6
5. The producer thread:
   - In a loop, puts incrementing uint32_t values into the message queue using k_msgq_put()
   - Sleeps 100ms between sends
   - Prints the sent value with printk
6. The consumer thread:
   - In a loop, gets messages from the queue using k_msgq_get() with K_FOREVER timeout
   - Prints the received value with printk
7. main() should just sleep forever with k_sleep(K_FOREVER)
8. Producer priority (5) must be numerically lower (higher priority) than consumer (6)

Use the Zephyr API: K_MSGQ_DEFINE, k_msgq_put, k_msgq_get, K_THREAD_DEFINE.

Include proper header: zephyr/kernel.h.

Output ONLY the complete C source file.
