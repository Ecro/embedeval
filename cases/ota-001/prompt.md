Write a Zephyr RTOS application that handles MCUboot image swap confirmation after an OTA update.

Requirements:
1. Include zephyr/kernel.h, zephyr/dfu/mcuboot.h
2. In main(), check if this is a new image after swap using boot_is_img_confirmed()
3. If NOT confirmed (newly swapped image):
   - Run a self-test (e.g., check a critical peripheral or flag)
   - If self-test passes, call boot_write_img_confirmed() to mark image as good
   - If self-test fails, print error and return (MCUboot will rollback on next reboot)
4. If already confirmed, print "Image already confirmed" and continue
5. Check return values of all boot_* API calls
6. Print status messages at each step with printk
7. Implement a simple self_test() function that returns 0 on success

This pattern prevents bricking: if a bad OTA image is flashed, failure to confirm
causes MCUboot to automatically roll back to the previous good image.

Output ONLY the complete C source file.
