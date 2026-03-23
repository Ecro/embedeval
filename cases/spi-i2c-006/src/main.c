#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/i2c.h>
#include <errno.h>

#define SENSOR_ADDR   0x48
#define READ_TIMEOUT  K_MSEC(100)
#define MAX_RETRIES   3

int main(void)
{
	const struct device *const i2c_dev = DEVICE_DT_GET(DT_NODELABEL(i2c0));
	uint8_t buf[2];
	int ret;

	if (!device_is_ready(i2c_dev)) {
		printk("I2C device not ready\n");
		return -ENODEV;
	}

	for (int attempt = 0; attempt < MAX_RETRIES; attempt++) {
		ret = i2c_read(i2c_dev, buf, sizeof(buf), SENSOR_ADDR);
		if (ret == 0) {
			printk("Sensor data: 0x%02x 0x%02x\n", buf[0], buf[1]);
			return 0;
		}

		if (ret == -ETIMEDOUT) {
			printk("I2C read timed out (attempt %d/%d)\n",
			       attempt + 1, MAX_RETRIES);
			k_sleep(K_MSEC(10));
		} else {
			printk("I2C read error: %d\n", ret);
			return ret;
		}
	}

	printk("I2C read failed after %d attempts: clock stretching timeout\n",
	       MAX_RETRIES);
	return -ETIMEDOUT;
}
