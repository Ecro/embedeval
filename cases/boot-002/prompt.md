Write a Zephyr Kconfig fragment that configures U-Boot as the bootloader with a boot delay and environment command support.

Requirements:
1. Do NOT enable CONFIG_BOOTLOADER_MCUBOOT (using U-Boot, not MCUboot)
2. Set CONFIG_BOOT_DELAY=3 (3 second boot delay)
3. Enable CONFIG_CMD_ENV=y (U-Boot environment variable commands)
4. Do NOT mix MCUboot-specific options (no CONFIG_MCUBOOT_IMG_MANAGER, no CONFIG_IMG_MANAGER)
5. Do NOT enable CONFIG_BOOT_UPGRADE_ONLY or CONFIG_BOOT_SIGNATURE_TYPE_RSA

Output ONLY the Kconfig fragment as plain text .conf file content.
