#include <zephyr/kernel.h>
#include <zephyr/drivers/uart.h>

static const struct device *uart_dev = DEVICE_DT_GET(DT_ALIAS(uart0));

int main(void)
{
	if (!device_is_ready(uart_dev)) {
		return -1;
	}

	unsigned char c;

	while (1) {
		if (uart_poll_in(uart_dev, &c) == 0) {
			uart_poll_out(uart_dev, c);
		}
	}

	return 0;
}
