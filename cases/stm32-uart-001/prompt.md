Write an STM32 HAL application that receives data via UART2 using interrupts.

Requirements:
1. Configure UART2 at 115200 baud, 8N1
2. Receive data using interrupt mode, not polling
3. Echo received bytes back via UART2
4. Handle UART errors appropriately
5. Include clock and GPIO configuration for UART pins (PA2 TX, PA3 RX)

Use STM32 HAL library for STM32F407.
Output ONLY the complete C source file.
