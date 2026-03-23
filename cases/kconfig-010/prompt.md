Write a Zephyr Kconfig fragment that enables PSA hardware crypto acceleration using MbedTLS.

Requirements:
1. Enable CONFIG_MBEDTLS=y (MbedTLS crypto library)
2. Enable CONFIG_MBEDTLS_BUILTIN=y (built-in MbedTLS implementation)
3. Enable CONFIG_MBEDTLS_PSA_CRYPTO_C=y (PSA Crypto API via MbedTLS)
4. Enable CONFIG_PSA_CRYPTO_DRIVER_CC3XX=y (Nordic CC3XX hardware crypto driver)
5. Enable CONFIG_HW_CC3XX=y (hardware CC3XX acceleration, depends on PSA_CRYPTO_DRIVER_CC3XX)
6. Do NOT enable CONFIG_TINYCRYPT=y (conflicts with MbedTLS backend — mutual exclusion)
7. Do NOT enable CONFIG_MBEDTLS_EXTERNAL=y alongside CONFIG_MBEDTLS_BUILTIN=y (mutually exclusive)
8. Do NOT enable CONFIG_TINYCRYPT_SHA256=y or any CONFIG_TINYCRYPT_* alongside MbedTLS

Output ONLY the Kconfig fragment as a plain text .conf file content.
