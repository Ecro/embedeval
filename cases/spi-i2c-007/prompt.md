Write a Zephyr RTOS application that performs a full-duplex SPI transfer, simultaneously transmitting and receiving data.

Requirements:
1. Get the SPI device using DEVICE_DT_GET(DT_NODELABEL(spi0))
2. Verify the device is initialized and ready before use
3. Define a TX buffer of 4 bytes with values {0x01, 0x02, 0x03, 0x04}
4. Define a separate RX buffer of 4 bytes initialized to zero — TX and RX must be different arrays
5. Create a spi_buf for TX and a separate spi_buf for RX, each pointing to their respective buffers
6. Create a spi_buf_set for TX (tx_bufs) and a separate spi_buf_set for RX (rx_bufs)
7. Configure spi_config with frequency = 1000000, operation = SPI_OP_MODE_MASTER | SPI_WORD_SET(8) | SPI_TRANSFER_MSB
8. Call spi_transceive() with both tx_bufs and rx_bufs populated
9. If spi_transceive() returns negative value, print error and return
10. Print the received bytes after successful transfer

Use the Zephyr SPI API: spi_transceive, DEVICE_DT_GET, DT_NODELABEL.
Do NOT use HAL_SPI_TransmitReceive() (STM32 HAL) or SPI.transfer() (Arduino).

Include proper headers: zephyr/kernel.h, zephyr/device.h, zephyr/drivers/spi.h.

Output ONLY the complete C source file.
