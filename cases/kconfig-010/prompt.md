Write a Zephyr RTOS Kconfig fragment (.conf) that enables hardware-accelerated cryptographic operations (AES, SHA, RNG) using the PSA Crypto API on a Nordic platform.

Requirements:
1. Use MbedTLS as the crypto backend (built-in implementation)
2. Enable the PSA Crypto API layer
3. Enable the Nordic CC3XX hardware crypto driver and its hardware acceleration
4. Do NOT enable TinyCrypt alongside MbedTLS (they are mutually exclusive crypto backends)
5. Do NOT enable external MbedTLS alongside built-in MbedTLS (mutually exclusive)

Output ONLY the Kconfig fragment as a plain text .conf file content.
