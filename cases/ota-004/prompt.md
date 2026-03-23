Write a Zephyr RTOS application that checks the running image version before accepting an OTA update.

Requirements:
1. Include zephyr/kernel.h, zephyr/dfu/mcuboot.h, zephyr/storage/flash_map.h
2. Define a struct representing the offered update version:
   - static const struct mcuboot_img_sem_ver offered = { .major=2, .minor=0, .revision=0, .build_num=0 };
3. In main():
   a. Declare struct mcuboot_img_header current_header
   b. Call boot_read_bank_header(FIXED_PARTITION_ID(slot0_partition), &current_header, sizeof(current_header)) and check return
   c. Get the running version from current_header.h1.v1.sem_ver
   d. Compare the offered version against the running version:
      - Compare major first, then minor, then revision
      - Only proceed if offered is strictly newer
   e. If offered is newer: print "Update accepted: %d.%d.%d → %d.%d.%d" and print "Proceeding with OTA"
   f. If offered is same or older: print "Update rejected: offered version not newer" and return 0
4. Always print the running version at startup: "Running version: %d.%d.%d"

Common mistakes: skipping version comparison (always updating), using wrong struct member names, ignoring byte-order.

Output ONLY the complete C source file.
