Write a Zephyr Kconfig fragment for MCUboot that enables debug-level logging and the boot banner.

Requirements:
1. Enable CONFIG_MCUBOOT_LOG_LEVEL_DBG=y (MCUboot debug log level)
2. Enable CONFIG_LOG=y (Zephyr logging subsystem, required for log level config)
3. Enable CONFIG_BOOT_BANNER=y (show boot banner message during startup)
4. Enable CONFIG_BOOTLOADER_MCUBOOT=y (MCUboot integration)
5. Do NOT enable CONFIG_LOG_MINIMAL=y (minimal logging disables the debug level output)

Output ONLY the Kconfig fragment as a plain text .conf file content.
