Write a Zephyr RTOS application that queries the status of both MCUboot image slots (primary and secondary).

Requirements:
1. Include zephyr/kernel.h, zephyr/dfu/mcuboot.h, zephyr/storage/flash_map.h
2. Query the swap type using mcuboot_swap_type()
3. For each slot (primary = FIXED_PARTITION_ID(slot0_partition), secondary = FIXED_PARTITION_ID(slot1_partition)):
   a. Call boot_read_bank_header(slot_id, &header, sizeof(header)) where header is struct mcuboot_img_header
   b. If the call returns 0: print the slot number, image version (header.h.v1.sem_ver), and size
   c. If the call returns non-zero: print "Slot N: empty or unreadable"
4. Print the swap type as a human-readable string:
   - BOOT_SWAP_TYPE_NONE → "No swap pending"
   - BOOT_SWAP_TYPE_TEST → "Test swap pending"
   - BOOT_SWAP_TYPE_PERM → "Permanent swap pending"
   - BOOT_SWAP_TYPE_REVERT → "Revert swap pending"
   - default → "Unknown swap type"
5. Print whether the current image is confirmed: boot_is_img_confirmed()

Requirements for correctness:
- Both slots must be checked (not just primary)
- Handle the case where secondary slot is empty (boot_read_bank_header returns non-zero)
- Version info must be extracted from the header struct (not hardcoded)

Output ONLY the complete C source file.
