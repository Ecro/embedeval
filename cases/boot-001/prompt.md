Write a Zephyr RTOS Kconfig fragment (.conf) that configures MCUboot integration for safe firmware updates with image confirmation support.

Requirements:
1. Enable MCUboot bootloader integration
2. Enable image management so the application can confirm or revert firmware images
3. Ensure all flash-related dependencies are enabled (flash subsystem, stream flash, etc.)
4. Set the image block buffer size to 512 bytes
5. Keep swap-based upgrade mode (do NOT enable upgrade-only mode, as it disables rollback)
6. Do NOT use single application slot (dual-slot is required for A/B updates)

Output ONLY the Kconfig fragment as plain text .conf file content.
