Implement a Zephyr RTOS application that safely shares a counter between an ISR and a reader thread.

Requirements:
1. Declare a shared counter variable accessible from both ISR and thread context
2. Implement an ISR handler that increments the shared counter with proper synchronization
3. Implement a reader thread that periodically reads and prints the counter value with proper synchronization
4. Use `k_spinlock` (NOT k_mutex, NOT irq_lock, NOT atomic_t) — save the key with `k_spinlock_key_t`, call `k_spin_lock()` in both ISR and thread contexts, and pass the saved key to `k_spin_unlock()`
5. In main(), simulate the ISR firing multiple times, then allow the reader thread time to complete
6. The reader thread should be defined statically with an appropriate stack size

Output ONLY the complete C source file.
