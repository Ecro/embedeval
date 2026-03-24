Write a Zephyr RTOS application that writes data to a SPI flash chip and reads it back for verification.

Requirements:
1. Get the SPI bus device using DEVICE_DT_GET(DT_NODELABEL(spi0))
2. Verify the device is initialized and ready before use
3. Configure struct spi_config with frequency 4000000, operation SPI_OP_MODE_MASTER | SPI_WORD_SET(8) | SPI_TRANSFER_MSB
4. Define a write buffer of 5 bytes: first byte is the Write command (0x02), next 3 bytes are the flash address (0x00, 0x00, 0x00), last byte is data (0xAB)
5. Send the Write Enable command (0x06) as a single byte before the write operation
6. Call spi_write() with the write buffer to program the flash
7. Poll the flash Status Register (read command 0x05, check bit 0 WIP) in a loop until the write completes; limit polling to 100 iterations to avoid infinite loop
8. Send a read command: byte 0x03 followed by address bytes 0x00, 0x00, 0x00, then receive 1 byte of data
9. Compare the read-back byte to 0xAB; print "Flash verify OK" or "Flash verify FAILED"
10. Check spi_write and spi_transceive return values for errors

Use the Zephyr SPI API: spi_write, spi_transceive, struct spi_buf, struct spi_buf_set.

Include proper headers: zephyr/kernel.h, zephyr/device.h, zephyr/drivers/spi.h, string.h.

Output ONLY the complete C source file.
