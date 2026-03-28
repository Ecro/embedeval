Write a Zephyr RTOS application implementing a reader-writer lock that allows multiple concurrent readers but exclusive writer access.

Requirements:
1. Implement read-lock and read-unlock functions that allow multiple readers to hold the lock simultaneously
2. Implement write-lock and write-unlock functions that provide exclusive access for a single writer
3. A writer must wait until all active readers have finished before acquiring the lock
4. Create at least 2 reader threads and 1 writer thread to demonstrate the pattern
5. Each thread should print messages showing when it acquires and releases the lock
6. In main(), initialize synchronization primitives and let the threads run

Output ONLY the complete C source file.
