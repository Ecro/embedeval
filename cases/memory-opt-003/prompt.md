Write a Zephyr RTOS application that demonstrates correct selection of K_HEAP_DEFINE (for variable-size allocations) versus K_MEM_SLAB_DEFINE (for fixed-size allocations).

Requirements:
1. Include zephyr/kernel.h and string.h
2. Define a heap with K_HEAP_DEFINE(my_heap, 1024) for variable-size use
3. Define a slab with K_MEM_SLAB_DEFINE(my_slab, 32, 8, 4) for fixed-size use
4. In main():
   a. Variable-size demo (use heap):
      - Allocate 100 bytes with k_heap_alloc(&my_heap, 100) using non-blocking allocation
      - Check for NULL (alloc failure)
      - Write data to the buffer
      - Print the pointer with printk
      - Free with k_heap_free(&my_heap, ptr)
   b. Fixed-size demo (use slab):
      - Allocate a block with k_mem_slab_alloc(&my_slab, &block) using non-blocking allocation
      - Check return value (< 0 means failure)
      - Write data to the block
      - Print number of used blocks with k_mem_slab_num_used_get
      - Free with k_mem_slab_free(&my_slab, block)
5. Add printk comments showing WHY each allocator was chosen for each use case

IMPORTANT: Never use K_MEM_SLAB for variable-size allocations — slab blocks are
fixed size. Never use K_HEAP for performance-critical fixed-size allocations —
slab is O(1) while heap is O(n). Always call the matching free function.

Output ONLY the complete C source file.
