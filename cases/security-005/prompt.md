Write a Zephyr application that stores and retrieves a secret using the PSA Protected Storage API (TF-M).

Requirements:
1. Include psa/protected_storage.h, psa/crypto.h, and zephyr/kernel.h
2. Call psa_crypto_init() and check the return value against PSA_SUCCESS
3. Define a non-zero UID (e.g. 42U) — UID 0 is reserved and must NOT be used
4. Define a static const secret buffer (e.g. "TopSecret\0", 10 bytes)
5. Store the secret using psa_ps_set(uid, data_length, data, PSA_STORAGE_FLAG_NONE)
6. Check psa_ps_set return value against PSA_SUCCESS
7. Declare a retrieve buffer of the same size as the secret
8. Retrieve the data using psa_ps_get(uid, 0, data_length, buffer, &actual_length)
9. Check psa_ps_get return value against PSA_SUCCESS
10. Verify retrieved data matches original using memcmp
11. Print "PS OK" if match, "PS FAILED" otherwise
12. Check all return values against PSA_SUCCESS

Output ONLY the complete C source file.
