Write a lock-free single-producer single-consumer (SPSC) ring queue in Zephyr RTOS using atomic operations.

Requirements:
1. Include zephyr/kernel.h and zephyr/sys/atomic.h
2. Define buffer size as a power of 2 (e.g., 16 or 32) — this enables bitwise masking instead of modulo
3. Define a struct spsc_queue with:
   - uint8_t buf[] array of the power-of-2 size
   - atomic_t write_idx  (producer advances this)
   - atomic_t read_idx   (consumer advances this)
4. Implement spsc_push(struct spsc_queue *q, uint8_t val):
   - Read write_idx with atomic_get
   - Check if full: (write - read) == SIZE (return -1 if full)
   - Write val to buf[write_idx & (SIZE-1)]
   - Advance write_idx with atomic_set
   - Return 0 on success
5. Implement spsc_pop(struct spsc_queue *q, uint8_t *val):
   - Read read_idx with atomic_get
   - Check if empty: read_idx == write_idx (return -1 if empty)
   - Read val from buf[read_idx & (SIZE-1)]
   - Advance read_idx with atomic_set
   - Return 0 on success
6. In main(): demonstrate push and pop, print results with printk

Constraints:
- NO k_mutex, NO k_sem, NO k_spin_lock — this is lock-free
- Use atomic_t for BOTH indices (not plain uint32_t)
- Buffer size MUST be a power of 2 (use bitwise mask & (SIZE-1), not modulo %)
- Memory barrier (compiler_barrier() or __dmb()) before advancing index

Output ONLY the complete C source file.
