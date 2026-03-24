Write an ESP-IDF application that communicates with an I2C sensor at address 0x68.

Requirements:
1. Initialize the I2C master bus on GPIO 21 (SDA) and GPIO 22 (SCL)
2. Set clock speed to 100kHz
3. Write a register address (0x75) to the device, then read 1 byte back
4. Print the read value
5. Handle errors appropriately
6. Clean up I2C resources when done

Use the ESP-IDF I2C driver API.
Output ONLY the complete C source file.
