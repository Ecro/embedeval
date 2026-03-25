Write an STM32 HAL application that enters Stop mode and wakes up via RTC alarm.

Requirements:
1. Configure RTC with an alarm to trigger after 5 seconds
2. Enter Stop mode using WFI
3. After wakeup, reconfigure the system clock (Stop mode disables PLL)
4. Indicate wakeup by toggling an LED (PD12)
5. Handle RTC alarm interrupt

Use STM32 HAL library for STM32F407.
Output ONLY the complete C source file.
