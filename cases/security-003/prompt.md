Write a Zephyr application that generates cryptographically secure random bytes using the PSA Crypto API and verifies the buffer is non-zero.

Requirements:
1. Include psa/crypto.h and zephyr/kernel.h
2. Call psa_crypto_init() and check the return value against PSA_SUCCESS
3. Declare a 32-byte buffer initialized to all zeros
4. Fill the buffer with random data using psa_generate_random()
5. Check all PSA API return values against PSA_SUCCESS
6. Verify the buffer is not all zeros (count non-zero bytes)
7. Print the number of non-zero bytes with printk
8. Print "RNG OK" if at least one byte is non-zero, "RNG FAILED" otherwise

Do NOT use rand(), srand(), or any standard C random functions.
Do NOT use sys_rand_get() or hardware-specific entropy APIs.
Use ONLY the PSA Crypto API (psa_generate_random).

Output ONLY the complete C source file.
