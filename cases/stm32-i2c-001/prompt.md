Write an STM32 HAL application that reads a WHO_AM_I register from an I2C sensor.

Requirements:
1. Configure I2C1 (PB6 SCL, PB7 SDA) at 100kHz
2. Read register 0x75 from device at address 0x68
3. Print the result (or store in a variable)
4. Handle communication errors
5. Check if the device is responding before reading

Use STM32 HAL library for STM32F407.
Output ONLY the complete C source file.
