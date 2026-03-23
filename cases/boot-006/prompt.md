Write a Zephyr Kconfig fragment for MCUboot that enables RSA image encryption with signature verification.

Requirements:
1. Enable CONFIG_BOOT_ENCRYPT_IMAGE=y (image encryption support)
2. Enable CONFIG_BOOT_ENCRYPT_RSA=y (RSA encryption for image keys, depends on BOOT_ENCRYPT_IMAGE)
3. Enable CONFIG_BOOT_SIGNATURE_TYPE_RSA=y (RSA signature verification, required by BOOT_ENCRYPT_RSA)
4. Set CONFIG_BOOT_SIGNATURE_KEY_FILE="root-rsa-2048.pem" (RSA key file path)
5. Do NOT enable CONFIG_BOOT_ENCRYPT_EC256=y alongside CONFIG_BOOT_ENCRYPT_RSA=y (mutually exclusive encryption types)
6. Do NOT enable CONFIG_BOOT_SIGNATURE_TYPE_ECDSA_P256=y with CONFIG_BOOT_SIGNATURE_TYPE_RSA=y (signature types are mutually exclusive)

Output ONLY the Kconfig fragment as a plain text .conf file content.
