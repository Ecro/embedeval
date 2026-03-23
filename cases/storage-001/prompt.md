Write a Zephyr RTOS application that stores and retrieves a value using NVS (Non-Volatile Storage).

Requirements:
1. Include zephyr/fs/nvs.h, zephyr/storage/flash_map.h, zephyr/kernel.h
2. Get the flash area using FIXED_PARTITION_DEVICE and FIXED_PARTITION_OFFSET for "storage_partition"
3. Define a struct nvs_fs and set:
   - flash_device to the partition device
   - offset to the partition offset
   - sector_size to 4096
   - sector_count to 2
4. Mount NVS with nvs_mount(), check return value
5. Define NVS_ID as 1
6. Write a uint32_t value (0xDEADBEEF) using nvs_write()
7. Read it back using nvs_read() into a separate variable
8. Verify the read value matches the written value
9. Print success or failure with printk
10. Handle all errors with return codes

Use the Zephyr NVS API: nvs_mount, nvs_write, nvs_read, struct nvs_fs.

Output ONLY the complete C source file.
