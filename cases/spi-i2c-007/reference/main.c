#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/spi.h>

static uint8_t tx_buf[4] = {0x01, 0x02, 0x03, 0x04};
static uint8_t rx_buf[4];

int main(void)
{
	const struct device *const spi_dev = DEVICE_DT_GET(DT_NODELABEL(spi0));
	int ret;

	if (!device_is_ready(spi_dev)) {
		printk("SPI device not ready\n");
		return -ENODEV;
	}

	const struct spi_buf tx_spi_buf = {
		.buf = tx_buf,
		.len = sizeof(tx_buf),
	};
	const struct spi_buf_set tx_bufs = {
		.buffers = &tx_spi_buf,
		.count = 1,
	};

	struct spi_buf rx_spi_buf = {
		.buf = rx_buf,
		.len = sizeof(rx_buf),
	};
	struct spi_buf_set rx_bufs = {
		.buffers = &rx_spi_buf,
		.count = 1,
	};

	const struct spi_config spi_cfg = {
		.frequency = 1000000,
		.operation = SPI_OP_MODE_MASTER | SPI_WORD_SET(8) | SPI_TRANSFER_MSB,
	};

	ret = spi_transceive(spi_dev, &spi_cfg, &tx_bufs, &rx_bufs);
	if (ret < 0) {
		printk("SPI transceive failed: %d\n", ret);
		return ret;
	}

	printk("SPI full-duplex OK. Received: 0x%02x 0x%02x 0x%02x 0x%02x\n",
	       rx_buf[0], rx_buf[1], rx_buf[2], rx_buf[3]);

	return 0;
}
