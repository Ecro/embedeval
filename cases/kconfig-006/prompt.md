Write a Zephyr Kconfig fragment that enables secure boot hardening for a production firmware image.

Requirements:
1. Enable CONFIG_STACK_CANARIES=y (software stack canary protection)
2. Enable CONFIG_HW_STACK_PROTECTION=y (hardware stack overflow detection)
3. Enable CONFIG_SECURE_BOOT=y (immutable bootloader secure boot chain)
4. Enable CONFIG_FW_INFO=y (required dependency for secure boot metadata)
5. Enable CONFIG_BOOTLOADER_MCUBOOT=y (MCUboot integration)
6. Do NOT enable CONFIG_DEBUG=y (disables optimizations, leaks info in production)
7. Do NOT enable CONFIG_ASSERT=y (assertion failures can expose internal state)
8. Do NOT enable CONFIG_SECURE_MODE=y
9. Do NOT enable CONFIG_DEBUG_OPTIMIZATIONS=y (production must not use debug build flags)

Output ONLY the Kconfig fragment as a plain text .conf file content.
