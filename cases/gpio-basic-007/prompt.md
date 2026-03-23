Write a Zephyr RTOS application that uses the asynchronous UART API with DMA support.

Requirements:
1. Get the UART device using DEVICE_DT_GET(DT_ALIAS(uart0)) and check it with device_is_ready()
2. Define a static RX buffer of at least 64 bytes
3. Register a UART callback using uart_callback_set(); the callback parameter type is uart_callback_t
4. In the callback, handle the UART_RX_RDY event: copy received data from evt->data.rx.buf + evt->data.rx.offset
5. Enable asynchronous RX using uart_rx_enable() with the RX buffer and a timeout of 100 (milliseconds)
6. Transmit a short greeting string using uart_tx() with SYS_FOREVER_US timeout
7. In main(), after setup, sleep forever with k_sleep(K_FOREVER)

Use ONLY the Zephyr async UART API: uart_callback_set, uart_tx, uart_rx_enable.
Do NOT use uart_poll_in(), uart_poll_out(), uart_read(), or uart_write() — those are either polling API or do not exist.

Include headers: zephyr/kernel.h, zephyr/device.h, zephyr/drivers/uart.h, string.h.

Output ONLY the complete C source file.
