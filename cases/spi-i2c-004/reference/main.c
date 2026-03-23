#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/spi.h>
#include <string.h>

#define FLASH_CMD_WREN  0x06
#define FLASH_CMD_WRITE 0x02
#define FLASH_CMD_RDSR  0x05
#define FLASH_CMD_READ  0x03
#define FLASH_WIP_BIT   0x01
#define FLASH_POLL_MAX  100
#define FLASH_DATA_BYTE 0xAB

static const struct spi_config spi_cfg = {
	.frequency = 4000000,
	.operation = SPI_OP_MODE_MASTER | SPI_WORD_SET(8) | SPI_TRANSFER_MSB,
};

static int flash_write_enable(const struct device *spi_dev)
{
	uint8_t cmd = FLASH_CMD_WREN;
	struct spi_buf buf = {.buf = &cmd, .len = 1};
	struct spi_buf_set tx = {.buffers = &buf, .count = 1};

	return spi_write(spi_dev, &spi_cfg, &tx);
}

static int flash_wait_ready(const struct device *spi_dev)
{
	uint8_t tx_data[2] = {FLASH_CMD_RDSR, 0x00};
	uint8_t rx_data[2] = {0};
	struct spi_buf tx_buf = {.buf = tx_data, .len = 2};
	struct spi_buf rx_buf = {.buf = rx_data, .len = 2};
	struct spi_buf_set tx_bufs = {.buffers = &tx_buf, .count = 1};
	struct spi_buf_set rx_bufs = {.buffers = &rx_buf, .count = 1};
	int ret;

	for (int i = 0; i < FLASH_POLL_MAX; i++) {
		ret = spi_transceive(spi_dev, &spi_cfg, &tx_bufs, &rx_bufs);
		if (ret < 0) {
			return ret;
		}
		if ((rx_data[1] & FLASH_WIP_BIT) == 0) {
			return 0;
		}
		k_sleep(K_MSEC(1));
	}
	return -ETIMEDOUT;
}

int main(void)
{
	const struct device *const spi_dev = DEVICE_DT_GET(DT_NODELABEL(spi0));
	int ret;

	if (!device_is_ready(spi_dev)) {
		printk("SPI device not ready\n");
		return -ENODEV;
	}

	/* Write enable */
	ret = flash_write_enable(spi_dev);
	if (ret < 0) {
		printk("Write enable failed: %d\n", ret);
		return ret;
	}

	/* Write: cmd + 3-byte addr + 1 data byte */
	uint8_t write_cmd[5] = {FLASH_CMD_WRITE, 0x00, 0x00, 0x00, FLASH_DATA_BYTE};
	struct spi_buf w_buf = {.buf = write_cmd, .len = sizeof(write_cmd)};
	struct spi_buf_set w_bufs = {.buffers = &w_buf, .count = 1};

	ret = spi_write(spi_dev, &spi_cfg, &w_bufs);
	if (ret < 0) {
		printk("Flash write failed: %d\n", ret);
		return ret;
	}

	/* Wait for write to complete */
	ret = flash_wait_ready(spi_dev);
	if (ret < 0) {
		printk("Flash busy-wait failed: %d\n", ret);
		return ret;
	}

	/* Read back: cmd + 3-byte addr, then receive 1 byte */
	uint8_t read_cmd[4] = {FLASH_CMD_READ, 0x00, 0x00, 0x00};
	uint8_t read_data = 0;
	struct spi_buf r_tx_buf = {.buf = read_cmd, .len = sizeof(read_cmd)};
	struct spi_buf r_rx_buf = {.buf = &read_data, .len = 1};
	struct spi_buf r_tx_set_bufs[2] = {
		{.buf = read_cmd, .len = sizeof(read_cmd)},
		{.buf = &read_data, .len = 1},
	};
	struct spi_buf r_rx_set_bufs[2] = {
		{.buf = NULL, .len = sizeof(read_cmd)},
		{.buf = &read_data, .len = 1},
	};

	(void)r_tx_buf;
	(void)r_rx_buf;

	struct spi_buf_set r_tx_bufs = {.buffers = r_tx_set_bufs, .count = 2};
	struct spi_buf_set r_rx_bufs = {.buffers = r_rx_set_bufs, .count = 2};

	ret = spi_transceive(spi_dev, &spi_cfg, &r_tx_bufs, &r_rx_bufs);
	if (ret < 0) {
		printk("Flash read failed: %d\n", ret);
		return ret;
	}

	if (read_data == FLASH_DATA_BYTE) {
		printk("Flash verify OK: 0x%02x\n", read_data);
	} else {
		printk("Flash verify FAILED: got 0x%02x, expected 0x%02x\n",
		       read_data, FLASH_DATA_BYTE);
		return -EIO;
	}

	return 0;
}
