Write a Zephyr RTOS application that implements OTA rollback with a confirmation timeout.

After booting into a newly swapped MCUboot image, the application must confirm the image within 60 seconds or the system resets (allowing MCUboot to roll back to the previous image).

Requirements:
1. Include zephyr/kernel.h, zephyr/dfu/mcuboot.h, zephyr/sys/reboot.h
2. Define CONFIRM_TIMEOUT_MS as 60000
3. Implement static int self_test(void) returning 0 on success
4. In main():
   a. Check boot_is_img_confirmed() — if already confirmed, print message and continue to app loop
   b. If NOT confirmed (newly swapped image):
      - Record deadline: int64_t deadline = k_uptime_get() + CONFIRM_TIMEOUT_MS
      - Run self_test(); if it fails, fall through to the reset path
      - Check if k_uptime_get() > deadline; if so, print "Rollback timeout — resetting" and call sys_reboot(SYS_REBOOT_COLD)
      - If self-test passed and within timeout: call boot_write_img_confirmed()
      - If boot_write_img_confirmed() fails: print error and call sys_reboot(SYS_REBOOT_COLD)
      - Print "Image confirmed" on success
   c. Run application main loop (k_sleep loop or similar)

Critical rules:
- The timer/deadline MUST be started as soon as the unconfirmed image is detected
- On timeout: call sys_reboot() — do NOT just log and continue
- Image must NOT be confirmed immediately on boot without self-test and timeout check
- Timeout value must be reasonable (between 5000 ms and 300000 ms)

Common mistakes:
- Calling boot_write_img_confirmed() immediately without any timeout check
- Using printk instead of sys_reboot on timeout (rollback never happens)
- Setting timeout to 0 or a negative value

Output ONLY the complete C source file.
