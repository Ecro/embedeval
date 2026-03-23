Write a Zephyr RTOS application that mounts a LittleFS filesystem, writes data to a file, and reads it back to verify.

Requirements:
1. Include zephyr/kernel.h, zephyr/fs/fs.h, and zephyr/fs/littlefs.h
2. Define a LittleFS mount point using FS_LITTLEFS_DECLARE_DEFAULT_CONFIG and struct fs_mount_t
3. Set the mount point path to "/lfs" and type to FS_LITTLEFS
4. Call fs_mount() before any file operations, check return value
5. Open a file at "/lfs/test.txt" using fs_open() with FS_O_CREATE | FS_O_RDWR flags
6. Write the string "hello" using fs_write(), check bytes written
7. Seek back to the beginning with fs_seek() before reading
8. Read back using fs_read() into a separate buffer
9. Close the file with fs_close() after all operations
10. Verify the read data matches written data, print success or failure with printk
11. Handle all errors with return codes

Use the Zephyr FS API: fs_mount, fs_open, fs_write, fs_seek, fs_read, fs_close.

Output ONLY the complete C source file.
