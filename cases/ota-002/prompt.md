Write a Zephyr RTOS application that reads and prints the current MCUboot swap type.

Requirements:
1. Include zephyr/kernel.h and zephyr/dfu/mcuboot.h
2. In main(), call mcuboot_swap_type() to get the current swap type
3. Use a switch statement (or equivalent) to print a human-readable status for ALL of these swap types:
   - BOOT_SWAP_TYPE_NONE   → print "Swap type: NONE"
   - BOOT_SWAP_TYPE_TEST   → print "Swap type: TEST"
   - BOOT_SWAP_TYPE_PERM   → print "Swap type: PERM"
   - BOOT_SWAP_TYPE_REVERT → print "Swap type: REVERT"
   - default/unknown       → print "Swap type: UNKNOWN (<value>)"
4. After printing the swap type, print "Boot status check complete"
5. Enter k_sleep(K_FOREVER)

The swap type indicates the boot state:
- NONE: normal boot, no pending swap
- TEST: a test image was swapped in (will revert unless confirmed)
- PERM: permanently upgraded
- REVERT: reverting to previous image

Output ONLY the complete C source file.
