Write a Zephyr RTOS application that performs an SPI loopback test.

Requirements:
1. Get the SPI bus device using DEVICE_DT_GET(DT_NODELABEL(spi0))
2. Verify the device is initialized and ready before use
3. Define a transmit buffer of 8 bytes initialized with a known pattern (e.g., 0x01 through 0x08)
4. Define a receive buffer of 8 bytes initialized to zero
5. Configure struct spi_config with frequency 1000000, operation SPI_OP_MODE_MASTER | SPI_WORD_SET(8)
6. Set up struct spi_buf for tx and rx, each pointing to their respective buffers with len = 8
7. Set up struct spi_buf_set for tx_bufs and rx_bufs, each with buf pointer and count = 1
8. Call spi_transceive() with the spi_config, tx_bufs, and rx_bufs
9. Check the return value for errors; print error and return on failure
10. Compare transmit and receive buffers byte-by-byte to verify loopback
11. Print "SPI loopback successful" on match, "SPI loopback mismatch" on failure

Use the Zephyr SPI API: spi_transceive, struct spi_config, struct spi_buf, struct spi_buf_set.

Include proper headers: zephyr/kernel.h, zephyr/device.h, zephyr/drivers/spi.h, string.h.

Output ONLY the complete C source file.
