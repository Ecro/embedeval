Write a Zephyr RTOS application that uses a memory slab for fixed-size block allocation without heap.

Requirements:
1. Define a memory slab using K_MEM_SLAB_DEFINE with:
   - Block size: 64 bytes
   - Number of blocks: 4
   - Alignment: 4 bytes
2. In main(), allocate a block using k_mem_slab_alloc() with a non-blocking timeout
3. Check the return value for allocation failure
4. Write some data to the allocated block (e.g., fill with a pattern)
5. Print the allocation success and address using printk
6. Free the block using k_mem_slab_free()
7. Print the number of used blocks using k_mem_slab_num_used_get()
8. Do NOT use malloc, calloc, k_malloc, or any heap allocation
9. Handle errors at each step

Use the Zephyr API: K_MEM_SLAB_DEFINE, k_mem_slab_alloc, k_mem_slab_free, k_mem_slab_num_used_get.

Include proper header: zephyr/kernel.h.

Output ONLY the complete C source file.
