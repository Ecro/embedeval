Write a Zephyr Kconfig fragment for MCUboot that enables serial recovery mode over USB CDC ACM.

Requirements:
1. Enable CONFIG_MCUBOOT_SERIAL=y (MCUboot serial recovery protocol)
2. Enable CONFIG_BOOT_SERIAL_CDC_ACM=y (CDC ACM USB transport for serial recovery)
3. Enable CONFIG_USB_DEVICE_STACK=y (USB device stack, required by CDC_ACM)
4. Enable CONFIG_USB_CDC_ACM=y (CDC ACM class driver)
5. Enable CONFIG_UART_LINE_CTRL=y (UART line control for CDC ACM)
6. Do NOT enable CONFIG_BOOT_SERIAL_UART=y alongside CONFIG_BOOT_SERIAL_CDC_ACM=y (transport types are mutually exclusive)

Output ONLY the Kconfig fragment as a plain text .conf file content.
