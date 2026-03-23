Write a Zephyr RTOS application that receives firmware chunks and writes them to flash using the dfu_target API.

Requirements:
1. Include zephyr/kernel.h, zephyr/dfu/mcuboot.h, zephyr/dfu/dfu_target.h
2. Define a simulated chunk buffer: static uint8_t chunk[256] and a total firmware size of 4096 bytes
3. In main(), implement the DFU write sequence:
   a. Call dfu_target_init(DFU_TARGET_IMAGE_TYPE_MCUBOOT, 0, total_size, NULL) and check return value
   b. Loop: write chunks by calling dfu_target_write(chunk, sizeof(chunk)) and check each return value
   c. After all chunks, call dfu_target_done(true) and check return value
   d. Print "DFU complete, resetting" then call sys_reboot(SYS_REBOOT_COLD)
4. On any error: call dfu_target_done(false) to abort, print the error, and return
5. Print progress: "Writing chunk %d/%d" for each chunk
6. Include zephyr/sys/reboot.h for sys_reboot

The correct sequence is: init → write chunks → done(true) → reboot.
Calling write before init, or omitting done(), are common mistakes.

Output ONLY the complete C source file.
