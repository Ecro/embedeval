Write a Zephyr application that implements wear-aware flash writes with sector rotation.

Requirements:
1. Include zephyr/drivers/flash.h, zephyr/storage/flash_map.h, and zephyr/kernel.h
2. Define at least 2 sectors with a per-sector write count array (e.g. static uint32_t write_count[NUM_SECTORS])
3. Define a WRITE_THRESHOLD (e.g. 100) — when a sector's write_count reaches this threshold, rotate to the next sector
4. Implement a function (e.g. wear_write) that:
   a. Checks the current sector's write_count against WRITE_THRESHOLD
   b. If threshold reached: increment to next sector (modulo NUM_SECTORS), erase the new sector with flash_erase(), reset its write count
   c. Write data to the current sector using flash_write()
   d. Increment the write_count for the current sector
5. Erase a sector with flash_erase() before writing to it (mandatory for flash)
6. Check return values of flash_erase() and flash_write()
7. Use DT_CHOSEN or FIXED_PARTITION macros to get the flash device
8. Call the wear_write function at least 3 times in main() with different data
9. Print "WEAR WRITE OK sector=<N> count=<N>" for each successful write
10. Print "WEAR WRITE FAILED" on any error

Output ONLY the complete C source file.
