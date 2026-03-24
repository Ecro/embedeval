Write a Linux kernel driver module that implements a safe ioctl handler.

Requirements:
1. Include linux/module.h, linux/fs.h, linux/uaccess.h, linux/ioctl.h
2. Define an ioctl command using _IOW or _IOR macro with a unique magic number
3. Implement an ioctl handler function with the signature:
   long my_ioctl(struct file *file, unsigned int cmd, unsigned long arg)
4. In the ioctl handler:
   - Validate _IOC_TYPE(cmd) matches your magic number, return -ENOTTY if mismatch
   - Validate _IOC_NR(cmd) is within the supported range, return -ENOTTY if out of range
   - Safely read ioctl arguments from user space (NOT direct pointer dereference)
   - Use access_ok() or rely on copy_from_user return value to validate user pointer
5. Define a struct for the ioctl argument (at least two fields)
6. Wire up the ioctl handler in file_operations as .unlocked_ioctl
7. Define MODULE_LICENSE("GPL"), MODULE_AUTHOR, MODULE_DESCRIPTION
8. Implement module_init and module_exit with proper cleanup

CRITICAL SECURITY RULES:
- NEVER dereference a __user pointer directly (e.g., val = *uarg is wrong)
- ALWAYS use the appropriate kernel API for user-space data transfer
- ALWAYS validate _IOC_TYPE before processing the command

Output ONLY the complete C source file.
