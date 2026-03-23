Write a Zephyr Kconfig fragment that configures MCUboot for a dual-core system with a main application image and a network core image.

Requirements:
1. Enable CONFIG_BOOTLOADER_MCUBOOT=y
2. Set CONFIG_BOOT_IMAGE_NUMBER=2 (two bootable images)
3. Set CONFIG_UPDATEABLE_IMAGE_NUMBER=2 (both images are updateable)
4. Enable CONFIG_PCD_APP=y (Peripheral CPU Domain app support for network core updates)
5. Enable CONFIG_FLASH=y (required for multi-image storage)
6. Do NOT set CONFIG_BOOT_IMAGE_NUMBER=1 (single-image, breaks dual-core)
7. Do NOT enable CONFIG_SINGLE_APPLICATION_SLOT (incompatible with multi-image)
8. Ensure CONFIG_BOOT_IMAGE_NUMBER and CONFIG_UPDATEABLE_IMAGE_NUMBER are consistent (both 2)

Output ONLY the Kconfig fragment as plain text .conf file content.
