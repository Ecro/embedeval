Write a Zephyr application that generates an ECDSA P-256 key pair using the PSA Crypto API and exports only the public key.

Requirements:
1. Include psa/crypto.h and zephyr/kernel.h
2. Call psa_crypto_init() and check the return value against PSA_SUCCESS
3. Initialize psa_key_attributes_t with PSA_KEY_ATTRIBUTES_INIT
4. Set key type to PSA_KEY_TYPE_ECC_KEY_PAIR(PSA_ECC_FAMILY_SECP_R1)
5. Set key bits to 256
6. Set algorithm to PSA_ALG_ECDSA(PSA_ALG_SHA_256)
7. Set usage flags to PSA_KEY_USAGE_SIGN_HASH — do NOT include PSA_KEY_USAGE_EXPORT
8. Generate the key pair using psa_generate_key() and check PSA_SUCCESS
9. Export the PUBLIC key using psa_export_public_key() (NOT psa_export_key)
10. Verify psa_export_key() (private key export) fails with PSA_ERROR_NOT_PERMITTED
11. Print "ECDSA KEY OK: pubkey_len=<N>" on success
12. Destroy the key with psa_destroy_key() when done
13. Check all PSA function return values against PSA_SUCCESS

Output ONLY the complete C source file.
