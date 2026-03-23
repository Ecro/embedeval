Write a Zephyr RTOS application that downloads an OTA image and reports download progress as a percentage.

Requirements:
1. Include zephyr/kernel.h, zephyr/dfu/dfu_target.h
2. Define constants:
   - CHUNK_SIZE 256
   - TOTAL_IMAGE_SIZE (must be a non-zero compile-time constant, e.g. 65536)
3. Implement static void report_progress(size_t received, size_t total):
   - If total == 0, print "Progress: unknown (total size not set)" and return
   - Otherwise compute: uint8_t pct = (uint8_t)((received * 100U) / total)
   - Print "OTA progress: %u%%" with the percentage
4. Implement static int ota_download(void):
   - Call dfu_target_init(DFU_TARGET_IMAGE_TYPE_MCUBOOT, 0, TOTAL_IMAGE_SIZE, NULL)
   - Loop over chunks: declare uint8_t chunk[CHUNK_SIZE], call dfu_target_write each iteration
   - Track size_t bytes_received, increment by CHUNK_SIZE each iteration
   - Call report_progress(bytes_received, TOTAL_IMAGE_SIZE) after each write
   - On dfu_target_write failure: print error, call dfu_target_done(false), return error
   - After all chunks written, call dfu_target_done(true) and return 0
5. In main(): call ota_download(), print result

Safety rules:
- TOTAL_IMAGE_SIZE must be known BEFORE the download loop starts — not computed after
- Division-by-zero: the total == 0 guard in report_progress is mandatory
- bytes_received must be a size_t (not uint8_t or uint16_t) to avoid overflow on large images

Output ONLY the complete C source file.
