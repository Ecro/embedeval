#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/spi.h>
#include <zephyr/drivers/gpio.h>

static uint8_t dev1_cmd = 0xAA;
static uint8_t dev2_cmd = 0xBB;

int main(void)
{
	const struct device *const spi_dev = DEVICE_DT_GET(DT_NODELABEL(spi0));
	const struct device *const gpio_dev = DEVICE_DT_GET(DT_NODELABEL(gpio0));
	int ret;

	if (!device_is_ready(spi_dev)) {
		printk("SPI device not ready\n");
		return -ENODEV;
	}

	if (!device_is_ready(gpio_dev)) {
		printk("GPIO device not ready\n");
		return -ENODEV;
	}

	const struct spi_config dev1_cfg = {
		.frequency = 1000000,
		.operation = SPI_OP_MODE_MASTER | SPI_WORD_SET(8),
		.cs = {
			.gpio = {
				.port = gpio_dev,
				.pin  = 10,
				.dt_flags = GPIO_ACTIVE_LOW,
			},
			.delay = 0,
		},
	};

	const struct spi_config dev2_cfg = {
		.frequency = 500000,
		.operation = SPI_OP_MODE_MASTER | SPI_WORD_SET(8),
		.cs = {
			.gpio = {
				.port = gpio_dev,
				.pin  = 11,
				.dt_flags = GPIO_ACTIVE_LOW,
			},
			.delay = 0,
		},
	};

	const struct spi_buf buf1 = { .buf = &dev1_cmd, .len = 1 };
	const struct spi_buf_set tx1 = { .buffers = &buf1, .count = 1 };

	ret = spi_write(spi_dev, &dev1_cfg, &tx1);
	printk("Device 1 write: %s (%d)\n", ret == 0 ? "OK" : "FAIL", ret);

	const struct spi_buf buf2 = { .buf = &dev2_cmd, .len = 1 };
	const struct spi_buf_set tx2 = { .buffers = &buf2, .count = 1 };

	ret = spi_write(spi_dev, &dev2_cfg, &tx2);
	printk("Device 2 write: %s (%d)\n", ret == 0 ? "OK" : "FAIL", ret);

	return 0;
}
