Write a Zephyr application that updates a configuration atomically using NVS to prevent data corruption on power loss.

Requirements:
1. Include zephyr/fs/nvs.h, zephyr/storage/flash_map.h, and zephyr/kernel.h
2. Define two NVS IDs: CONFIG_ID_PRIMARY (e.g. 1) and CONFIG_ID_TEMP (e.g. 2)
3. Define a config struct with at least 2 fields (e.g. uint32_t version, uint32_t value)
4. Mount NVS with nvs_mount(), check the return value
5. Implement atomic update as follows (write-then-commit pattern):
   a. Write new config to CONFIG_ID_TEMP using nvs_write()
   b. Check nvs_write() return value
   c. Read back from CONFIG_ID_TEMP using nvs_read() and verify the readback matches
   d. Only if verification passes: write to CONFIG_ID_PRIMARY using nvs_write()
   e. Delete CONFIG_ID_TEMP using nvs_delete() after successful commit
6. Do NOT write directly to CONFIG_ID_PRIMARY in-place (that is not atomic)
7. Print "CONFIG COMMIT OK" after successful atomic update
8. Print "CONFIG COMMIT FAILED: verify mismatch" if readback doesn't match
9. Handle the case where CONFIG_ID_TEMP already exists (from a previous interrupted write)
   by checking nvs_read() return value on startup

Output ONLY the complete C source file.
