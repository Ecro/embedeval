Write a Zephyr RTOS application that manages two SPI devices on the same bus, each with a dedicated chip-select GPIO pin.

Requirements:
1. Get the shared SPI bus device using DEVICE_DT_GET(DT_NODELABEL(spi0))
2. Check device readiness with device_is_ready()
3. Configure device 1 with its own spi_config:
   - frequency = 1000000
   - operation = SPI_OP_MODE_MASTER | SPI_WORD_SET(8)
   - cs.gpio: GPIO device from DT_NODELABEL(gpio0), pin 10, GPIO_ACTIVE_LOW
4. Configure device 2 with its own spi_config:
   - frequency = 500000
   - operation = SPI_OP_MODE_MASTER | SPI_WORD_SET(8)
   - cs.gpio: same GPIO device, pin 11, GPIO_ACTIVE_LOW (DIFFERENT pin from device 1)
5. Write a 1-byte command 0xAA to device 1 using spi_write()
6. Write a 1-byte command 0xBB to device 2 using spi_write()
7. Print result of each transfer

Use the Zephyr SPI API with spi_cs_control for manual CS management.

Include proper headers: zephyr/kernel.h, zephyr/device.h, zephyr/drivers/spi.h, zephyr/drivers/gpio.h.

Output ONLY the complete C source file.
