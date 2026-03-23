Write a Zephyr RTOS application demonstrating deadlock-free multi-mutex acquisition using lock ordering.

Requirements:
1. Include zephyr/kernel.h
2. Declare two mutexes: mutex_a and mutex_b, both initialized with K_MUTEX_DEFINE
3. Implement thread_one() that:
   - Locks mutex_a FIRST, then mutex_b (in that order)
   - Does some work (printk "Thread one working")
   - Unlocks mutex_b FIRST, then mutex_a (reverse order)
4. Implement thread_two() that:
   - Also locks mutex_a FIRST, then mutex_b (SAME order as thread_one)
   - Does some work (printk "Thread two working")
   - Unlocks mutex_b FIRST, then mutex_a (reverse order)
5. Both threads repeat in a loop
6. In main(): threads are already started via K_THREAD_DEFINE, sleep forever

CRITICAL DEADLOCK PREVENTION RULE:
Both threads MUST acquire locks in the SAME ORDER (always A then B, never B then A).
Acquiring in opposite orders creates circular wait (classic deadlock).

Do NOT use:
- pthread_mutex_lock (POSIX, not Zephyr)
- xSemaphoreTake (FreeRTOS, not Zephyr)
- k_sem_take as a mutex replacement (use k_mutex for mutual exclusion)

Use the Zephyr API: K_MUTEX_DEFINE, k_mutex_lock, k_mutex_unlock with K_FOREVER timeout.

Output ONLY the complete C source file.
