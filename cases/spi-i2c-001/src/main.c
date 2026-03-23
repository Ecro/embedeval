#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/i2c.h>

#define SENSOR_ADDR 0x68
#define WHO_AM_I_REG 0x75

int main(void)
{
	const struct device *const i2c_dev = DEVICE_DT_GET(DT_NODELABEL(i2c0));
	uint8_t who_am_i;
	int ret;

	if (!device_is_ready(i2c_dev)) {
		printk("I2C device not ready\n");
		return -ENODEV;
	}

	ret = i2c_reg_read_byte(i2c_dev, SENSOR_ADDR, WHO_AM_I_REG, &who_am_i);
	if (ret < 0) {
		printk("Failed to read WHO_AM_I: %d\n", ret);
		return ret;
	}

	printk("WHO_AM_I: 0x%02x\n", who_am_i);
	return 0;
}
