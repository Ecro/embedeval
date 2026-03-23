Write a Zephyr Kconfig fragment that enables SPI with DMA mode. The fragment should:
1. Enable CONFIG_SPI=y
2. Enable CONFIG_SPI_DMA=y (which depends on SPI)
3. Enable CONFIG_DMA=y (dependency for SPI_DMA)
4. NOT enable conflicting options

Output ONLY the Kconfig fragment as a plain text .conf file content.
