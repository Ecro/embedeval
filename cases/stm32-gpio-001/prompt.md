Write an STM32 HAL application for STM32F407 that toggles an LED when a button is pressed.

Requirements:
1. Configure PD12 as output for LED
2. Configure PA0 as input with external interrupt (rising edge)
3. Toggle the LED in the interrupt callback
4. Include proper GPIO initialization with clock enable
5. Enter an infinite loop in main after setup

Use STM32 HAL library. Include stm32f4xx_hal.h.
Output ONLY the complete C source file.
