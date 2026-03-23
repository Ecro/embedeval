Write a Zephyr Kconfig fragment that enables USB CDC ACM serial communication. The fragment should:
1. Enable CONFIG_USB_DEVICE_STACK=y (USB device stack base)
2. Enable CONFIG_USB_CDC_ACM=y (depends on USB_DEVICE_STACK)
3. Enable CONFIG_UART_LINE_CTRL=y (line control for CDC ACM)
4. NOT enable conflicting options

Output ONLY the Kconfig fragment as a plain text .conf file content.
