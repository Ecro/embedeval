Write a Zephyr RTOS application that applies a binary delta (differential) OTA patch to produce an updated image.

Requirements:
1. Include zephyr/kernel.h, zephyr/dfu/mcuboot.h, zephyr/dfu/dfu_target.h, zephyr/sys/crc.h
2. Define constants:
   - SOURCE_SIZE 4096 (current image size)
   - PATCH_SIZE  512  (delta patch size)
   - TARGET_SIZE 4096 (resulting image size)
3. Declare simulated buffers:
   - static uint8_t source_image[SOURCE_SIZE]
   - static uint8_t patch_data[PATCH_SIZE]
   - static uint8_t target_image[TARGET_SIZE]
4. Implement static int verify_patch_integrity(const uint8_t *patch, size_t len, uint32_t expected_crc):
   - Compute CRC32 of the patch using crc32_ieee(patch, len)
   - Return 0 if CRC matches expected_crc, -EBADMSG otherwise
5. Implement static int apply_patch(const uint8_t *src, size_t src_len, const uint8_t *patch, size_t patch_len, uint8_t *target, size_t target_len):
   - Copy source to target: memcpy(target, src, src_len)
   - Apply patch bytes XOR over target: for each patch byte, target[i % target_len] ^= patch[i]
   - Return 0 on success
6. In main():
   a. Define uint32_t expected_patch_crc = crc32_ieee(patch_data, PATCH_SIZE) — simulate knowing the expected CRC
   b. Call verify_patch_integrity() FIRST — if it fails, print "Patch integrity check failed — aborting" and return error
   c. Only after integrity verified: call apply_patch()
   d. If apply_patch succeeds: call dfu_target_init, dfu_target_write(target_image, TARGET_SIZE), dfu_target_done(true)
   e. If any step fails: call dfu_target_done(false) and return error

Critical ordering rule:
- verify_patch_integrity() MUST be called before apply_patch() and before any dfu_target_write
- If patch verification fails, do NOT write anything to flash

Output ONLY the complete C source file.
