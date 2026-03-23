Implement a Zephyr RTOS double-buffer (ping-pong) pattern where an ISR fills one buffer while a thread processes the other, using an atomic index to track which buffer is active.

Requirements:
1. Include zephyr/kernel.h and zephyr/sys/atomic.h
2. Define a buffer size constant (e.g. BUF_SIZE 8)
3. Declare two uint32_t buffers: buf[2][BUF_SIZE]
4. Declare an atomic_t write_idx initialized to 0 (ISR writes to this buffer index)
5. Implement an ISR function (isr_handler) that:
   - Reads current write index with atomic_get(&write_idx)
   - Fills buf[write_idx] with sample data (e.g. sequential values)
   - Atomically swaps write_idx to the other buffer: atomic_set(&write_idx, 1 - current)
   - Does NOT access the same buffer index the thread is processing
6. Implement a processor thread function that:
   - Reads the buffer NOT currently being written: process_idx = 1 - atomic_get(&write_idx)
   - Sums values in buf[process_idx]
   - Prints the sum with printk
   - Sleeps 50ms between iterations
   - Loops at least 4 times
7. Define the processor thread with K_THREAD_DEFINE and a stack of at least 1024 bytes
8. In main(), simulate 3 ISR firings, sleep briefly, then allow thread to process

Output ONLY the complete C source file.
