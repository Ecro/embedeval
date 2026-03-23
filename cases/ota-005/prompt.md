Write a Zephyr RTOS application implementing a complete OTA update flow with rollback safety using a state machine.

Requirements:
1. Include zephyr/kernel.h, zephyr/dfu/mcuboot.h, zephyr/dfu/dfu_target.h, zephyr/sys/reboot.h
2. Define an enum for OTA states:
   - OTA_IDLE, OTA_DOWNLOADING, OTA_VERIFYING, OTA_REBOOTING, OTA_CONFIRMING
3. Implement state transition functions, one per state:
   - ota_do_download(): simulate download, call dfu_target_init then dfu_target_write in a loop, transition to VERIFYING on success
   - ota_do_verify(): verify image integrity (check return of dfu_target_done(true)), transition to REBOOTING on success
   - ota_do_reboot(): print "Rebooting to test new image", call sys_reboot(SYS_REBOOT_COLD)
   - ota_do_confirm(): called after reboot in new image — check boot_is_img_confirmed(), if not confirmed run self-test then call boot_write_img_confirmed(); implement a confirm timeout: if confirmation does not succeed within 30 seconds, do NOT confirm (allow MCUboot rollback)
4. In main(), drive the state machine with a while loop:
   - Print the current state name on each transition
   - Handle errors: on any failure, log error and return to OTA_IDLE
5. Implement static int self_test(void) returning 0 on success
6. The confirm step MUST happen after reboot (check boot_is_img_confirmed() first)

Critical safety rules:
- NEVER confirm before self-test passes
- NEVER skip the VERIFYING state (dfu_target_done must be called before reboot)
- A rollback timeout must exist: if confirmation hangs, MCUboot rolls back

Output ONLY the complete C source file.
