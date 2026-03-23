Write a Zephyr application that generates cryptographically secure random bytes, checking entropy availability before use.

Requirements:
1. Include zephyr/kernel.h and zephyr/random/random.h
2. Do NOT use rand(), srand(), or sys_rand_get() — these are not cryptographically secure
3. Use sys_csrand_get() to fill a 32-byte buffer with secure random data
4. Check the return value of sys_csrand_get() — it returns 0 on success, negative errno on failure
5. If sys_csrand_get() fails with -EINVAL or any negative return, print an error and return
6. Print "RNG OK: " followed by the first 4 bytes of the buffer in hex on success
7. Print "RNG FAILED: <error_code>" on failure
8. Alternatively, psa_generate_random() from psa/crypto.h is also acceptable as the random source
9. Generate at least 32 bytes of random data

Output ONLY the complete C source file.
