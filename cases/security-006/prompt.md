Write a Zephyr application that imports an AES-128 key into PSA Crypto with anti-tamper (non-extractable) attributes.

Requirements:
1. Include psa/crypto.h and zephyr/kernel.h
2. Call psa_crypto_init() and check the return value against PSA_SUCCESS
3. Define a 16-byte AES key material as a static const uint8_t array
4. Set key type to PSA_KEY_TYPE_AES
5. Set key bits to 128
6. Set key algorithm to PSA_ALG_CBC_NO_PADDING or PSA_ALG_ECB_NO_PADDING
7. Set key lifetime to PSA_KEY_LIFETIME_PERSISTENT
8. Set a non-zero key ID (e.g. PSA_KEY_ID_USER_MIN or a literal like 1U)
9. Set key usage to PSA_KEY_USAGE_ENCRYPT only — do NOT include PSA_KEY_USAGE_EXPORT
10. Import the key using psa_import_key() and check the return value against PSA_SUCCESS
11. Verify the key is non-extractable: call psa_export_key() and confirm it returns PSA_ERROR_NOT_PERMITTED
12. Print "KEY SECURE" if export is denied, "KEY EXPOSED" if export succeeds (security failure)
13. Destroy the key with psa_destroy_key() when done

Output ONLY the complete C source file.
