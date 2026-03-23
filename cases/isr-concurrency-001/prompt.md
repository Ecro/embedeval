Implement an ISR-safe ring buffer in C for Zephyr RTOS. The ring buffer must:
1. Allow ISR context to produce (write) data
2. Allow thread context to consume (read) data
3. Be lock-free (no mutexes -- use atomic operations)
4. Handle buffer full and empty conditions
5. Maintain FIFO ordering

Provide the complete implementation with header and source.
