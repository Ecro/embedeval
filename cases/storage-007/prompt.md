Write a Zephyr application that mounts a LittleFS filesystem with automatic format-and-remount error recovery.

Requirements:
1. Include zephyr/fs/fs.h, zephyr/fs/littlefs.h, zephyr/storage/flash_map.h, and zephyr/kernel.h
2. Define a struct fs_mount_t configured for LittleFS (type = FS_LITTLEFS)
3. Set the mount point to "/lfs" and storage_dev to the fixed partition device
4. Attempt to mount with fs_mount() and check the return value
5. If fs_mount() fails (returns negative):
   a. Print a warning: "Mount failed, formatting..."
   b. Call fs_mkfs() with FS_LITTLEFS type to format the partition
   c. Check fs_mkfs() return value — print error and return on failure
   d. Call fs_mount() again and check the return value
   e. Print error and return if second mount also fails
6. On successful mount, print "FS MOUNTED OK"
7. After successful mount, write a test file using fs_open()/fs_write()/fs_close()
8. Do NOT simply return an error on first mount failure (LLM failure: no recovery)

Output ONLY the complete C source file.
