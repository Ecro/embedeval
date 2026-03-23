Write a Zephyr RTOS application that erases a flash area sector, writes data to it, and reads back to verify.

Requirements:
1. Include zephyr/kernel.h and zephyr/storage/flash_map.h
2. Open the "storage_partition" flash area using flash_area_open() with FIXED_PARTITION_ID
3. Erase the first sector (offset 0, size 4096) using flash_area_erase() before any writes
4. Write a uint32_t value (0xCAFEBABE) at offset 0 using flash_area_write()
5. Read back the value using flash_area_read() into a separate variable
6. Close the flash area with flash_area_close() after all operations
7. Verify read value matches written value, print success or failure with printk
8. Handle all errors with return codes; do NOT write without erasing first

Use the Zephyr Flash Area API: flash_area_open, flash_area_erase, flash_area_write, flash_area_read, flash_area_close.

Output ONLY the complete C source file.
