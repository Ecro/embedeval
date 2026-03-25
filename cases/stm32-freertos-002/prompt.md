Write an STM32 HAL + FreeRTOS application where an ISR sends data to a task.

Requirements:
1. Configure a timer interrupt (TIM2) at 10Hz
2. In the timer callback, send a value to a task using an ISR-safe mechanism
3. A receiving task waits for and processes the data
4. Use proper synchronization between ISR and task
5. Do not use blocking calls in the ISR

Use STM32 HAL + FreeRTOS for STM32F407.
Output ONLY the complete C source file.
