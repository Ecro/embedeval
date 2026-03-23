Write a Zephyr RTOS application that downloads an OTA image and verifies its SHA-256 hash before writing to flash.

Requirements:
1. Include zephyr/kernel.h, zephyr/dfu/mcuboot.h, zephyr/dfu/dfu_target.h, psa/crypto.h
2. Define constants:
   - IMAGE_SIZE (4096 bytes)
   - A uint8_t expected_hash[32] array (the pre-known SHA-256 of the image)
3. Implement static int compute_hash(const uint8_t *data, size_t len, uint8_t *out_hash):
   - Use psa_hash_compute(PSA_ALG_SHA_256, data, len, out_hash, 32, &hash_len)
   - Return 0 on success, negative on error
   - Do NOT implement a custom SHA-256 algorithm — use psa_hash_compute
4. Implement static int verify_hash(const uint8_t *computed, const uint8_t *expected):
   - Compare 32 bytes using memcmp
   - Return 0 if match, -EBADMSG if mismatch
5. In main():
   a. Simulate download: declare uint8_t image_buf[IMAGE_SIZE] and populate it
   b. Call compute_hash() on image_buf BEFORE any flash write
   c. Call verify_hash() to compare with expected_hash
   d. ONLY IF hash matches: call dfu_target_init, dfu_target_write, dfu_target_done(true)
   e. If hash mismatch: print "Hash mismatch — aborting OTA" and return error
   f. If hash or DFU calls fail: print error and return

Critical ordering rule:
- Hash MUST be computed and verified BEFORE any dfu_target_write call
- Writing to flash before verifying the hash is a security and correctness bug

Output ONLY the complete C source file.
