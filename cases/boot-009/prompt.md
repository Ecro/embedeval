Write a Zephyr Kconfig fragment for MCUboot that enables dual-bank boot using SPI NOR external flash as the secondary slot.

Requirements:
1. Enable CONFIG_PM_EXTERNAL_FLASH_MCUBOOT_SECONDARY=y (use external flash for MCUboot secondary slot)
2. Enable CONFIG_SPI_NOR=y (SPI NOR flash driver)
3. Set CONFIG_SPI_NOR_FLASH_LAYOUT_PAGE_SIZE=4096 (page size for external NOR flash layout)
4. Enable CONFIG_FLASH=y (flash subsystem, required by SPI_NOR)
5. Enable CONFIG_FLASH_MAP=y (flash map support required for multi-slot layout)
6. Enable CONFIG_STREAM_FLASH=y (streaming flash write support)
7. Do NOT enable CONFIG_SINGLE_APPLICATION_SLOT=y (incompatible with dual-bank external flash)

Output ONLY the Kconfig fragment as a plain text .conf file content.
