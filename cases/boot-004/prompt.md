Write a Zephyr Kconfig fragment that enables MCUboot swap-move mode with automatic revert capability.

Requirements:
1. Enable CONFIG_BOOTLOADER_MCUBOOT=y
2. Enable CONFIG_BOOT_SWAP_USING_MOVE=y (move-based swap algorithm)
3. Set CONFIG_BOOT_MAX_IMG_SECTORS=128 (must be at least 128 for typical flash layouts)
4. Enable CONFIG_FLASH=y (required for swap operations)
5. Do NOT enable CONFIG_BOOT_UPGRADE_ONLY=y (conflicts with swap/revert mode)
6. Do NOT enable CONFIG_SINGLE_APPLICATION_SLOT (requires dual-slot layout for swap)

Output ONLY the Kconfig fragment as plain text .conf file content.
