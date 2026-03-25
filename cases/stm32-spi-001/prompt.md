Write an STM32 HAL application that communicates with an SPI device as master.

Requirements:
1. Configure SPI1 (PA5 SCK, PA6 MISO, PA7 MOSI)
2. Use a GPIO pin (PB0) as chip select (manual control)
3. Write a command byte then read a response byte
4. Handle SPI errors
5. Assert CS low before transfer, high after

Use STM32 HAL library for STM32F407.
Output ONLY the complete C source file.
