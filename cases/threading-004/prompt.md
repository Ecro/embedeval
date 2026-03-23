Write a Zephyr RTOS application demonstrating priority inheritance with a mutex.

Requirements:
1. Include zephyr/kernel.h
2. Define a mutex using K_MUTEX_DEFINE (k_mutex has priority inheritance built-in)
3. Define three thread entry functions: low_prio_entry, med_prio_entry, high_prio_entry
4. Create three threads using K_THREAD_DEFINE:
   - low_prio_thread: stack 1024, priority 10 (lowest priority, runs first, holds mutex)
   - med_prio_thread: stack 1024, priority 7 (medium priority, should NOT preempt low while it holds mutex)
   - high_prio_thread: stack 1024, priority 4 (highest priority, tries to acquire mutex)
5. low_prio_entry:
   - Locks the mutex with k_mutex_lock() using K_FOREVER
   - Prints "Low: holding mutex" using printk
   - Sleeps 300ms (simulates work while holding mutex)
   - Prints "Low: releasing mutex" using printk
   - Unlocks the mutex with k_mutex_unlock()
6. med_prio_entry:
   - Sleeps 50ms (starts after low acquires mutex)
   - Prints "Med: running (should not preempt low)" using printk
   - Loops forever sleeping 100ms
7. high_prio_entry:
   - Sleeps 100ms (starts after low has mutex)
   - Tries to lock the mutex with k_mutex_lock() using K_FOREVER
   - Prints "High: acquired mutex" after lock succeeds
   - Unlocks the mutex immediately
8. main() sleeps forever with k_sleep(K_FOREVER)

Use k_mutex (NOT k_sem) because only k_mutex provides priority inheritance.

Use the Zephyr API: K_MUTEX_DEFINE, k_mutex_lock, k_mutex_unlock, K_THREAD_DEFINE.

Output ONLY the complete C source file.
