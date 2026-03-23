Write a Zephyr RTOS application that transfers data from an ISR to a thread using k_fifo.

Requirements:
1. Include zephyr/kernel.h
2. Define a data item struct with a void *fifo_reserved field as first member (required by k_fifo)
3. Statically allocate a pool of data items (use a static array, NOT k_malloc)
4. Declare and initialize a k_fifo using K_FIFO_DEFINE
5. Implement an ISR handler that:
   - Takes a statically allocated item from the pool
   - Fills in the data field
   - Calls k_fifo_put() to enqueue the item (non-blocking, ISR-safe)
   - Does NOT call k_fifo_get() (blocking, forbidden in ISR)
   - Does NOT call k_malloc() or any allocator
6. Implement a consumer thread that:
   - Calls k_fifo_get() with a timeout to dequeue items
   - Processes each item and prints it with printk
7. In main(), start the consumer thread and return

The ISR MUST NOT call k_fifo_get() — it blocks.
The ISR MUST NOT call k_malloc() — heap allocation is forbidden in ISR context.
Items MUST be statically allocated (static array pool).
Do NOT use FreeRTOS APIs (no xQueueSendFromISR, no xQueueReceive).

Use the Zephyr API: K_FIFO_DEFINE, k_fifo_put, k_fifo_get, K_THREAD_DEFINE or k_thread_create.

Output ONLY the complete C source file.
