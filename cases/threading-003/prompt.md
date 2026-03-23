Write a Zephyr RTOS application using a semaphore for event signaling between a producer and consumer thread.

Requirements:
1. Include zephyr/kernel.h
2. Define a binary semaphore using K_SEM_DEFINE with initial count 0 and maximum count 1
3. Create a producer thread using K_THREAD_DEFINE with stack size 1024 and priority 5
4. Create a consumer thread using K_THREAD_DEFINE with stack size 1024 and priority 6
5. The producer thread:
   - Loops 5 times
   - Sleeps 200ms
   - Calls k_sem_give() to signal the event
   - Prints "Producer: event signaled" using printk
6. The consumer thread:
   - Loops 5 times
   - Calls k_sem_take() with K_FOREVER timeout to wait for the event
   - Prints "Consumer: event received" using printk
7. main() sleeps forever with k_sleep(K_FOREVER)

The semaphore initial count MUST be 0 (not 1) so the consumer blocks until the producer signals.
The consumer MUST use K_FOREVER (not K_NO_WAIT) to block properly.

Use the Zephyr API: K_SEM_DEFINE, k_sem_give, k_sem_take, K_FOREVER.

Output ONLY the complete C source file.
