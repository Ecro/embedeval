Write a Zephyr application that computes an HMAC-SHA256 message authentication code using the PSA Crypto MAC API.

Requirements:
1. Include psa/crypto.h and zephyr/kernel.h
2. Call psa_crypto_init() and check the return value against PSA_SUCCESS
3. Define a static const uint8_t HMAC key (at least 32 bytes)
4. Define a static const uint8_t message to authenticate
5. Import the HMAC key using psa_import_key() with:
   - Type: PSA_KEY_TYPE_HMAC
   - Algorithm: PSA_ALG_HMAC(PSA_ALG_SHA_256)
   - Usage: PSA_KEY_USAGE_SIGN_MESSAGE
6. Initialize a psa_mac_operation_t with PSA_MAC_OPERATION_INIT
7. Call psa_mac_sign_setup() with the key handle and PSA_ALG_HMAC(PSA_ALG_SHA_256)
8. Call psa_mac_update() with the message buffer
9. Call psa_mac_sign_finish() to obtain the MAC output
10. Check all PSA function return values against PSA_SUCCESS
11. Do NOT use psa_hash_setup/psa_hash_update/psa_hash_finish (those are for plain hashing, not HMAC)
12. Print "HMAC OK" followed by the first 4 bytes of the MAC in hex, or "HMAC FAILED" on error
13. Destroy the key and abort the operation on any error path

Output ONLY the complete C source file.
