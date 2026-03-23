#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/i2c.h>

#define I2C_SCAN_ADDR_MIN 0x08
#define I2C_SCAN_ADDR_MAX 0x77

int main(void)
{
	const struct device *const i2c_dev = DEVICE_DT_GET(DT_NODELABEL(i2c0));
	int found = 0;
	int ret;

	if (!device_is_ready(i2c_dev)) {
		printk("I2C device not ready\n");
		return -ENODEV;
	}

	printk("Scanning I2C bus...\n");

	for (uint8_t addr = I2C_SCAN_ADDR_MIN; addr <= I2C_SCAN_ADDR_MAX; addr++) {
		ret = i2c_write(i2c_dev, NULL, 0, addr);
		if (ret == 0) {
			printk("Found device at 0x%02x\n", addr);
			found++;
		}
	}

	printk("Scan complete: %d device(s) found\n", found);

	return 0;
}
