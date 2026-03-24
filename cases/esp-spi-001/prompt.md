Write an ESP-IDF application that performs an SPI master half-duplex write to an SPI device.

Requirements:
1. Initialize the SPI bus on HSPI_HOST (SPI2_HOST) with MOSI on GPIO 23, SCLK on GPIO 18, CS on GPIO 5
2. Add an SPI device with clock speed 1 MHz
3. Transmit 4 bytes of data (0x01, 0x02, 0x03, 0x04) in a single transaction
4. Handle all error return values with esp_err_t checks
5. Print the result of the transfer

Use spi_bus_initialize, spi_bus_add_device, and spi_device_transmit.
Include proper headers.
Output ONLY the complete C source file.
