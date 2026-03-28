Write a Zephyr RTOS application that allocates and frees fixed-size memory blocks without using the heap.

Requirements:
1. Set up a pool of 4 blocks, each 64 bytes, with 4-byte alignment
2. Allocate a block from the pool (non-blocking)
3. Check the return value for allocation failure
4. Write some data to the allocated block
5. Print the allocation success and block address
6. Free the block back to the pool
7. Print how many blocks are currently in use
8. Do not use malloc, calloc, k_malloc, or any heap-based allocation
9. Handle errors at each step

Include only zephyr/kernel.h.

Output ONLY the complete C source file.
