Write a minimal Linux kernel character device driver module.

Requirements:
1. Include linux/module.h, linux/fs.h, linux/cdev.h, linux/uaccess.h
2. Define MODULE_LICENSE("GPL"), MODULE_AUTHOR, MODULE_DESCRIPTION
3. Define a static char buffer (256 bytes) for device data storage
4. Implement file_operations with:
   - .open: print device opened with pr_info, return 0
   - .release: print device closed with pr_info, return 0
   - .read: copy data from kernel buffer to user space using copy_to_user()
   - .write: copy data from user space to kernel buffer using copy_from_user()
5. In module_init:
   - Allocate a character device region with alloc_chrdev_region()
   - Initialize cdev with cdev_init()
   - Add cdev with cdev_add()
   - Create device class and device for auto /dev node creation
   - Print the major number with pr_info
6. In module_exit:
   - Remove cdev, destroy device, destroy class
   - Unregister the character device region
7. Use module_init() and module_exit() macros

IMPORTANT: Use copy_to_user/copy_from_user, NEVER access user pointers directly.

Output ONLY the complete C source file.
