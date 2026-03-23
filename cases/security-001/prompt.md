Write a Zephyr application that encrypts and decrypts data using the PSA Crypto API with AES-256-CBC.

Requirements:
1. Include psa/crypto.h and zephyr/kernel.h
2. Call psa_crypto_init() and check return value (must be PSA_SUCCESS)
3. Define a 32-byte (256-bit) AES key as a static const array
4. Import the key using psa_import_key() with:
   - Key type: PSA_KEY_TYPE_AES
   - Algorithm: PSA_ALG_CBC_NO_PADDING
   - Usage flags: PSA_KEY_USAGE_ENCRYPT | PSA_KEY_USAGE_DECRYPT
   - Key bits: 256
5. Define a 16-byte plaintext input (must be AES block-aligned)
6. Encrypt using psa_cipher_encrypt() and store in output buffer
7. Decrypt the ciphertext using psa_cipher_decrypt() and store in result buffer
8. Compare the decrypted result with the original plaintext
9. Destroy the key with psa_destroy_key() after use
10. Print success/failure with printk
11. Handle all PSA errors with return value checks

Output ONLY the complete C source file.
