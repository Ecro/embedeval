Write an STM32 HAL + FreeRTOS application with a producer and consumer task communicating via a queue.

Requirements:
1. Create a producer task that sends incrementing numbers to a queue every 500ms
2. Create a consumer task that receives from the queue and processes the data
3. Use appropriate stack sizes for each task
4. Set different priorities (producer lower, consumer higher)
5. Start the FreeRTOS scheduler

Use STM32 HAL + FreeRTOS (CMSIS-RTOS v2 or native API).
Output ONLY the complete C source file.
