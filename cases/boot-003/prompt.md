Write a Zephyr Kconfig fragment that enables MCUboot with RSA signing and slot0 validation for secure boot.

Requirements:
1. Enable CONFIG_BOOTLOADER_MCUBOOT=y
2. Enable CONFIG_BOOT_SIGNATURE_TYPE_RSA=y (RSA signature verification)
3. Set CONFIG_BOOT_SIGNATURE_KEY_FILE="my_key.pem" (path to signing key)
4. Enable CONFIG_BOOT_VALIDATE_SLOT0=y (validate the primary slot on every boot)
5. Enable CONFIG_FLASH=y (required for image storage)
6. Do NOT omit signature type or key file (insecure configuration)
7. Do NOT set CONFIG_BOOT_VALIDATE_SLOT0=n or omit it

Output ONLY the Kconfig fragment as plain text .conf file content.
