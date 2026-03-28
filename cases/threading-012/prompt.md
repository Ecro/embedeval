Write a Zephyr RTOS application that continuously reads a sensor, filters the data, and outputs results over UART.

Requirements:
1. Read a sensor value every 100ms
2. Apply a moving average filter over the last 10 samples
3. Send the filtered result over UART every 1 second
4. The sensor read must never be delayed by UART transmission
5. Structure the application with appropriate task decomposition for a real-time embedded system
6. Include proper initialization and error handling

Provide the complete main.c implementation.
