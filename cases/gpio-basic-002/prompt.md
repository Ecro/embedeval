Write a Zephyr RTOS application that reads bytes from a UART device and echoes them back.

Requirements:
1. Get the UART device from devicetree alias "uart0" using DEVICE_DT_GET(DT_ALIAS(uart0))
2. Verify the device is ready using device_is_ready()
3. In main(), loop forever reading bytes with uart_poll_in() and echoing them with uart_poll_out()
4. uart_poll_in() returns 0 on success, negative on no data — only echo when a byte is successfully read
5. Use a tight polling loop (no sleep needed between polls)

Use the Zephyr UART poll API (uart_poll_in, uart_poll_out).

Include proper headers: zephyr/kernel.h and zephyr/drivers/uart.h.

Output ONLY the complete C source file.
