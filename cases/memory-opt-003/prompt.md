Write a Zephyr RTOS application that demonstrates two different dynamic memory allocation strategies: one for variable-size allocations and one for fixed-size allocations.

Requirements:
1. Include zephyr/kernel.h and string.h
2. Set up both a variable-size allocator (total pool: 1024 bytes) and a fixed-size block allocator (block size: 32 bytes, 8 blocks, 4-byte alignment)
3. Variable-size demo:
   - Allocate 100 bytes (non-blocking)
   - Check for allocation failure
   - Write data to the buffer and print the pointer
   - Free the allocation
4. Fixed-size demo:
   - Allocate one block (non-blocking)
   - Check for allocation failure
   - Write data to the block and print how many blocks are in use
   - Free the block
5. Print a message explaining why each allocator was chosen for its use case

Output ONLY the complete C source file.
