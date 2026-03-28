Write a minimal Linux kernel character device driver module.

Requirements:
1. Define proper module metadata (license, author, description)
2. Provide a static kernel buffer (256 bytes) for device data storage
3. Implement file operations: open, release, read, and write
4. The read and write operations must safely transfer data between kernel and user space
5. In module init, register the character device with dynamic major number allocation and create a device node automatically
6. In module exit, clean up all registered resources in the correct order
7. Print the assigned major number on initialization

Output ONLY the complete C source file.
