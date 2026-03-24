Implement a Zephyr RTOS application that protects shared state between an ISR and a thread using k_spinlock.

Requirements:
1. Include zephyr/kernel.h
2. Declare a shared uint32_t counter variable
3. Implement an ISR function (isr_handler) that:
   - Uses ISR-safe synchronization to protect the shared counter (note: k_mutex_lock is forbidden in ISR context)
   - Increments the shared counter
   - Saves and restores interrupt state when accessing shared data
4. Implement a reader thread function that:
   - Loops 5 times
   - Each iteration: acquires the same synchronization primitive, reads counter, releases it
   - Prints the counter value with printk
   - Sleeps 100ms between reads with k_sleep(K_MSEC(100))
5. Define the reader thread with K_THREAD_DEFINE and a stack of at least 1024 bytes
6. In main(), simulate ISR firing 5 times by calling isr_handler() directly
7. Call k_sleep(K_MSEC(600)) in main to allow reader thread to complete

Output ONLY the complete C source file.
