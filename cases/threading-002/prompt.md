Write a Zephyr RTOS application where two threads increment a shared counter protected by a mutex.

Requirements:
1. Include zephyr/kernel.h
2. Define a global uint32_t shared counter initialized to 0
3. Define a mutex using K_MUTEX_DEFINE
4. Create two threads using K_THREAD_DEFINE, each with stack size 1024 and priorities 5 and 6
5. Each thread entry function must:
   - Loop 5 times
   - Lock the mutex with k_mutex_lock() using K_FOREVER
   - Increment the shared counter
   - Print the new counter value and which thread incremented it using printk
   - Unlock the mutex with k_mutex_unlock()
   - Sleep 50ms between iterations
6. main() prints "Final counter:" followed by the counter value, then returns 0
7. The mutex MUST be unlocked in all code paths (no missing unlock)

Use the Zephyr API: K_MUTEX_DEFINE, k_mutex_lock, k_mutex_unlock, K_THREAD_DEFINE.

Output ONLY the complete C source file.
