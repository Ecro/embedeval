Write a Zephyr RTOS application that implements shared-memory IPC between a producer and consumer using a memory-mapped shared region.

Requirements:
1. Define a shared memory region accessible by both producer and consumer
2. The producer writes sensor data into the shared region periodically
3. The consumer reads and processes the data when new data is available
4. Implement a handshake mechanism using flags in the shared region (not kernel synchronization primitives across the boundary)
5. Ensure data consistency — the consumer must never read partially written data
6. The shared memory structure must have proper alignment for hardware access

Provide the complete main.c implementation.
