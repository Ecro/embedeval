Write a Zephyr Kconfig fragment for MCUboot that enables downgrade protection using build number version comparison.

Requirements:
1. Enable CONFIG_BOOT_VERSION_CMP_USE_BUILD_NUMBER=y (use build number in version comparison for downgrade detection)
2. Enable CONFIG_BOOT_VALIDATE_SLOT0=y (validate primary slot before booting, required for downgrade protection to work)
3. Enable CONFIG_IMGMGR_VERBOSE_ERR=y (verbose error reporting for image manager)
4. Enable CONFIG_BOOTLOADER_MCUBOOT=y (MCUboot integration)
5. Enable CONFIG_BOOT_UPGRADE_ONLY=y (prevent reverting to older images once upgraded)
6. Do NOT enable CONFIG_SINGLE_APPLICATION_SLOT=y (incompatible with upgrade protection)

Output ONLY the Kconfig fragment as a plain text .conf file content.
