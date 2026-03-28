#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/uart.h>
#include <string.h>

static uint8_t rx_buf[64];
static const char tx_msg[] = "Hello UART async\r\n";

static void uart_cb(const struct device *dev, struct uart_event *evt, void *user_data)
{
	switch (evt->type) {
	case UART_RX_RDY:
		/* Process received bytes */
		(void)evt->data.rx.buf;
		(void)evt->data.rx.offset;
		(void)evt->data.rx.len;
		break;
	case UART_RX_BUF_REQUEST:
		break;
	case UART_RX_BUF_RELEASED:
		break;
	case UART_RX_DISABLED:
		break;
	default:
		break;
	}
}

int main(void)
{
	const struct device *uart = DEVICE_DT_GET(DT_ALIAS(uart0));

	if (!device_is_ready(uart)) {
		return -1;
	}

	uart_callback_set(uart, uart_cb, NULL);
	uart_rx_enable(uart, rx_buf, sizeof(rx_buf), 100);
	uart_tx(uart, (const uint8_t *)tx_msg, strlen(tx_msg), SYS_FOREVER_US);

	k_sleep(K_FOREVER);
	return 0;
}
