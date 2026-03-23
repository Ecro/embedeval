Write a Zephyr Device Tree overlay that adds a SPI NOR flash node (compatible "jedec,spi-nor") on the spi0 bus. The flash uses chip select 0 (reg = <0>), a maximum SPI frequency of 1MHz (spi-max-frequency = <1000000>), and a size of 1MB (size = <0x100000>). Set status = "okay" on both the flash node and the spi0 bus.

Output ONLY the Device Tree overlay (.overlay file content).
