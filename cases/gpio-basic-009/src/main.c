#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/uart.h>
#include <string.h>

static void uart_send_str(const struct device *uart, const char *str)
{
	while (*str) {
		uart_poll_out(uart, *str++);
	}
}

int main(void)
{
	const struct device *uart0 = DEVICE_DT_GET(DT_ALIAS(uart0));
	const struct device *uart1 = DEVICE_DT_GET(DT_ALIAS(uart1));

	if (!device_is_ready(uart0) || !device_is_ready(uart1)) {
		return -1;
	}

	struct uart_config cfg0 = {
		.baudrate = 115200,
		.parity = UART_CFG_PARITY_NONE,
		.stop_bits = UART_CFG_STOP_BITS_1,
		.data_bits = UART_CFG_DATA_BITS_8,
		.flow_ctrl = UART_CFG_FLOW_CTRL_NONE,
	};

	int err = uart_configure(uart0, &cfg0);

	if (err < 0) {
		printk("uart0 configure failed: %d\n", err);
		return -1;
	}

	struct uart_config cfg1 = {
		.baudrate = 9600,
		.parity = UART_CFG_PARITY_NONE,
		.stop_bits = UART_CFG_STOP_BITS_1,
		.data_bits = UART_CFG_DATA_BITS_8,
		.flow_ctrl = UART_CFG_FLOW_CTRL_NONE,
	};

	err = uart_configure(uart1, &cfg1);
	if (err < 0) {
		printk("uart1 configure failed: %d\n", err);
		return -1;
	}

	uart_send_str(uart0, "Hello on uart0 at 115200\r\n");

	/* Change uart1 baudrate at runtime */
	cfg1.baudrate = 38400;
	err = uart_configure(uart1, &cfg1);
	if (err < 0) {
		printk("uart1 reconfigure failed: %d\n", err);
		return -1;
	}

	uart_send_str(uart1, "Hello on uart1 at 38400\r\n");

	k_sleep(K_FOREVER);
	return 0;
}
