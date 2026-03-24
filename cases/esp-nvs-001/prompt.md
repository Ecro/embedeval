Write an ESP-IDF application that reads and writes an integer value to Non-Volatile Storage (NVS).

Requirements:
1. Initialize NVS flash with nvs_flash_init (handle ESP_ERR_NVS_NO_FREE_PAGES by erasing and reinitializing)
2. Open an NVS namespace "storage" with NVS_READWRITE
3. Try to read an existing counter value with key "counter"; if not found, start at 0
4. Increment the counter value
5. Write the new counter value with nvs_set_i32
6. Commit the changes with nvs_commit before closing
7. Close the NVS handle with nvs_close
8. Print the counter value

Use the ESP-IDF NVS API.
Include proper headers.
Output ONLY the complete C source file.
