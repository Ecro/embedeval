Write a Zephyr application that validates flash area boundaries before writing to prevent out-of-bounds flash access.

Requirements:
1. Include zephyr/storage/flash_map.h, zephyr/drivers/flash.h, and zephyr/kernel.h
2. Open a flash area using flash_area_open() with FIXED_PARTITION_ID
3. Get the flash area size using flash_area_get_size()
4. Before any flash write, validate:
   a. offset >= 0
   b. size > 0
   c. offset + size <= area_size (the critical boundary check)
5. If boundary check fails, print "BOUNDARY VIOLATION: offset=<N> size=<N> area=<N>" and return an error
6. Perform the write using flash_area_write() only if boundary check passes
7. Always call flash_area_close() when done (even on error paths)
8. Attempt at least one valid write (within bounds) and one invalid write (beyond bounds) to demonstrate
9. Print "WRITE OK" for valid writes, "WRITE BLOCKED" for boundary violations
10. Check all return values

Output ONLY the complete C source file.
