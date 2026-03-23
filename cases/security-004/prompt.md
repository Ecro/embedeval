Write a Zephyr application that derives a 32-byte key from a password using HKDF-SHA-256 via the PSA Key Derivation API.

Requirements:
1. Include psa/crypto.h and zephyr/kernel.h
2. Call psa_crypto_init() and check the return value against PSA_SUCCESS
3. Define static const arrays for:
   - password (input key material, e.g. "my-secret-password")
   - salt (e.g. 16 bytes of 0x01..0x10)
   - info (context label, e.g. "key-derivation-v1")
4. Declare a 32-byte output buffer for the derived key
5. Use the PSA key derivation operation in this exact order:
   a. psa_key_derivation_operation_t op = PSA_KEY_DERIVATION_OPERATION_INIT
   b. psa_key_derivation_setup(&op, PSA_ALG_HKDF(PSA_ALG_SHA_256))
   c. psa_key_derivation_input_bytes(&op, PSA_KEY_DERIVATION_INPUT_SALT, salt, salt_len)
   d. psa_key_derivation_input_bytes(&op, PSA_KEY_DERIVATION_INPUT_SECRET, password, password_len)
   e. psa_key_derivation_input_bytes(&op, PSA_KEY_DERIVATION_INPUT_INFO, info, info_len)
   f. psa_key_derivation_output_bytes(&op, derived_key, sizeof(derived_key))
   g. psa_key_derivation_abort(&op)
6. Check all PSA API return values against PSA_SUCCESS
7. Print the first 4 bytes of derived_key as hex with printk
8. Print "HKDF OK" on success

Output ONLY the complete C source file.
