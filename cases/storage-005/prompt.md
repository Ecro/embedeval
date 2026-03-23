Write a Zephyr RTOS application that demonstrates NVS wear-leveling awareness by writing multiple entries, deleting old ones, checking remaining space, and handling storage exhaustion gracefully.

Requirements:
1. Include zephyr/fs/nvs.h, zephyr/storage/flash_map.h, and zephyr/kernel.h
2. Define struct nvs_fs with sector_size=4096 and sector_count=2 (small, to trigger wear awareness)
3. Mount NVS with nvs_mount(), check return value
4. Write 3 distinct NVS entries (IDs 1, 2, 3) with different uint32_t values
5. Call nvs_calc_free_space() after writes and print the result with printk
6. Delete entry with ID 1 using nvs_delete()
7. Call nvs_calc_free_space() again to show space reclaimed, print the result
8. Attempt a write in a loop and handle -ENOSPC return gracefully (print warning, do not abort)
9. Check free space before large writes; if insufficient, print a warning and skip
10. Handle all errors with return codes

Use: nvs_mount, nvs_write, nvs_delete, nvs_calc_free_space. Handle errno -ENOSPC explicitly.

Output ONLY the complete C source file.
