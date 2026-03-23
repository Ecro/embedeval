Implement a fixed-size object pool in C that avoids heap allocation entirely.

Requirements:
1. Include zephyr/kernel.h (or standard C headers if needed)
2. Define a pool object type with at least two fields (e.g., id and data buffer)
3. Create a static array of pool objects (not heap-allocated):
   static struct my_obj pool[POOL_SIZE];
4. Implement a free list using an index array or embedded next pointer:
   - Track which objects are available without malloc
5. Implement pool_alloc() function:
   - Returns a pointer to an available object, or NULL if pool is exhausted
   - Updates the free list to mark the object as used
6. Implement pool_free(struct my_obj *obj) function:
   - Returns the object to the pool by updating the free list
   - Validates the pointer is within the pool bounds before freeing
7. In main():
   - Allocate several objects from the pool
   - Verify NULL is returned when pool is exhausted
   - Free objects and verify they can be re-allocated

CRITICAL: Do NOT use malloc(), calloc(), k_malloc(), or k_calloc() anywhere.
All memory must come from the static pool array defined at compile time.

Output ONLY the complete C source file.
