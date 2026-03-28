Write a Zephyr RTOS application that transfers structured data from an ISR to a consumer thread using a FIFO queue.

Requirements:
1. Define a data item struct suitable for FIFO usage
2. Use statically allocated data items — no dynamic memory allocation
3. Implement an ISR handler that enqueues data items into the FIFO
4. Implement a consumer thread that dequeues and prints items from the FIFO
5. In main(), start the consumer thread and simulate ISR events

Output ONLY the complete C source file.
