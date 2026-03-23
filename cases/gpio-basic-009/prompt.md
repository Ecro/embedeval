Write a Zephyr RTOS application that configures two UART devices with different baudrates and changes one baudrate at runtime.

Requirements:
1. Get uart0 using DEVICE_DT_GET(DT_ALIAS(uart0)) and uart1 using DEVICE_DT_GET(DT_ALIAS(uart1))
2. Call device_is_ready() on BOTH UARTs; return -1 if either fails
3. Configure uart0 at 115200 baud using uart_configure() with a struct uart_config:
   - baudrate = 115200, parity = UART_CFG_PARITY_NONE
   - stop_bits = UART_CFG_STOP_BITS_1, data_bits = UART_CFG_DATA_BITS_8
   - flow_ctrl = UART_CFG_FLOW_CTRL_NONE
4. Configure uart1 at 9600 baud using the same struct but baudrate = 9600
5. Check that the uart_configure() return values are not negative; print an error and return if they fail
6. Send a short string on uart0 at 115200 using uart_poll_out() in a loop over each character
7. Change uart1 baudrate to 38400 at runtime: call uart_configure() again with baudrate = 38400
8. Send a second string on uart1 at the new baudrate using uart_poll_out()
9. After setup, sleep forever with k_sleep(K_FOREVER)

Use ONLY Zephyr UART APIs. Include: zephyr/kernel.h, zephyr/device.h, zephyr/drivers/uart.h, string.h.

Output ONLY the complete C source file.
