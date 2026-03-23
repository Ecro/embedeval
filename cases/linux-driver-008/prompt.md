Write a Linux kernel module that creates a /proc entry to expose driver status information.

Requirements:
1. Include linux/module.h, linux/proc_fs.h, linux/seq_file.h
2. Define MODULE_LICENSE("GPL"), MODULE_AUTHOR, MODULE_DESCRIPTION
3. Implement a show function with signature:
   static int my_show(struct seq_file *m, void *v)
   - Use seq_printf() to write at least two status lines (e.g., "status: active\n", "count: %d\n")
   - Return 0 on success
4. Implement an open function using single_open():
   static int my_open(struct inode *inode, struct file *file)
5. Define struct proc_ops with:
   - .proc_open pointing to your open function
   - .proc_read = seq_read
   - .proc_lseek = seq_lseek
   - .proc_release = single_release
6. In module_init:
   - Call proc_create() to register the /proc entry
   - Check return value and return -ENOMEM on failure
7. In module_exit:
   - Call proc_remove() to unregister the /proc entry

IMPORTANT: Use struct proc_ops (NOT struct file_operations for /proc in modern kernels).
Use seq_printf() to write to the proc file — NEVER use sprintf to write directly to a user buffer.

Output ONLY the complete C source file.
