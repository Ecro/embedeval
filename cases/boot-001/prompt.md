Write a Zephyr Kconfig fragment that enables MCUboot bootloader integration with image confirmation.

Requirements:
1. Enable CONFIG_BOOTLOADER_MCUBOOT=y
2. Enable CONFIG_MCUBOOT_IMG_MANAGER=y (image management support)
3. Enable CONFIG_IMG_MANAGER=y (required dependency)
4. Enable CONFIG_FLASH=y (required for image storage)
5. Enable CONFIG_STREAM_FLASH=y (required for flash streaming)
6. Enable CONFIG_IMG_BLOCK_BUF_SIZE=512 (image block buffer size)
7. Do NOT enable CONFIG_BOOT_UPGRADE_ONLY (keep swap mode for rollback)
8. Do NOT enable CONFIG_SINGLE_APPLICATION_SLOT

Output ONLY the Kconfig fragment as plain text .conf file content.
