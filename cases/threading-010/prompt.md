Write a Zephyr RTOS application implementing a reader-writer lock pattern allowing multiple concurrent readers but exclusive writer access.

Requirements:
1. Include zephyr/kernel.h
2. Implement a rwlock struct or use globals:
   - k_mutex write_mutex: held exclusively during writes and while readers are changing count
   - k_sem reader_sem: binary semaphore (limit=1) for write-excluding reader protection
   - int reader_count: number of active readers (protected by write_mutex)
3. Implement rwlock_read_lock():
   - Lock write_mutex
   - Increment reader_count
   - If reader_count == 1: k_sem_take(&reader_sem, K_FOREVER) — first reader blocks writers
   - Unlock write_mutex
4. Implement rwlock_read_unlock():
   - Lock write_mutex
   - Decrement reader_count
   - If reader_count == 0: k_sem_give(&reader_sem) — last reader unblocks writers
   - Unlock write_mutex
5. Implement rwlock_write_lock(): k_sem_take(&reader_sem, K_FOREVER)
6. Implement rwlock_write_unlock(): k_sem_give(&reader_sem)
7. Implement 2 reader threads and 1 writer thread demonstrating the pattern
8. In main(): initialize mutex and semaphore (sem initial=1, limit=1), start threads

KEY INVARIANTS:
- Multiple readers can be active simultaneously (reader_count can be > 1)
- Writer waits for ALL readers to finish before getting exclusive access
- reader_sem initial count MUST be 1 (not 0) — writer takes it to exclude readers

Output ONLY the complete C source file.
