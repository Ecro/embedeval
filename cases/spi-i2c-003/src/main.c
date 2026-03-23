#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/i2c.h>

#define ACCEL_ADDR    0x19
#define ACCEL_OUT_X_L 0x28
#define ACCEL_DATA_LEN 6

int main(void)
{
	const struct device *const i2c_dev = DEVICE_DT_GET(DT_NODELABEL(i2c0));
	uint8_t raw[ACCEL_DATA_LEN];
	int ret;

	if (!device_is_ready(i2c_dev)) {
		printk("I2C device not ready\n");
		return -ENODEV;
	}

	ret = i2c_burst_read(i2c_dev, ACCEL_ADDR, ACCEL_OUT_X_L, raw, ACCEL_DATA_LEN);
	if (ret < 0) {
		printk("Burst read failed: %d\n", ret);
		return ret;
	}

	int16_t x = (int16_t)((raw[1] << 8) | raw[0]);
	int16_t y = (int16_t)((raw[3] << 8) | raw[2]);
	int16_t z = (int16_t)((raw[5] << 8) | raw[4]);

	printk("Accel X: %d  Y: %d  Z: %d\n", x, y, z);

	return 0;
}
