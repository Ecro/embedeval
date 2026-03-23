#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/spi.h>
#include <string.h>

#define SPI_FREQ 1000000

static uint8_t tx_buf[8] = {0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08};
static uint8_t rx_buf[8];

int main(void)
{
	const struct device *const spi_dev = DEVICE_DT_GET(DT_NODELABEL(spi0));
	int ret;

	if (!device_is_ready(spi_dev)) {
		printk("SPI device not ready\n");
		return -ENODEV;
	}

	memset(rx_buf, 0, sizeof(rx_buf));

	const struct spi_config spi_cfg = {
		.frequency = SPI_FREQ,
		.operation = SPI_OP_MODE_MASTER | SPI_WORD_SET(8),
	};

	struct spi_buf tx_spi_buf = {
		.buf = tx_buf,
		.len = sizeof(tx_buf),
	};
	struct spi_buf_set tx_bufs = {
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

	ret = spi_transceive(spi_dev, &spi_cfg, &tx_bufs, &rx_bufs);
	if (ret < 0) {
		printk("SPI transceive failed: %d\n", ret);
		return ret;
	}

	if (memcmp(tx_buf, rx_buf, sizeof(tx_buf)) == 0) {
		printk("SPI loopback successful\n");
	} else {
		printk("SPI loopback mismatch\n");
		return -EIO;
	}

	return 0;
}
