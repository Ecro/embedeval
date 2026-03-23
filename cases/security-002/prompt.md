Write a Zephyr application that computes a SHA-256 hash of a known message using the PSA Crypto API and verifies it matches the expected digest.

Requirements:
1. Include psa/crypto.h and zephyr/kernel.h
2. Call psa_crypto_init() and check the return value against PSA_SUCCESS
3. Define a static const message buffer (e.g. "Hello Zephyr")
4. Define a static const expected_hash array containing the correct 32-byte SHA-256 digest of your message
5. Declare a 32-byte output buffer for the computed hash
6. Compute the hash using psa_hash_compute() with PSA_ALG_SHA_256
7. Compare the computed hash against the expected_hash using memcmp
8. Print success ("SHA-256 OK") or failure ("SHA-256 FAILED") with printk
9. Check all PSA API return values against PSA_SUCCESS

Output ONLY the complete C source file.
