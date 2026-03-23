#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/i2c.h>

#define DEV_ADDR    0x3C
#define REG_ADDR    0x10
#define DATA_LEN    4

int main(void)
{
	const struct device *const i2c_dev = DEVICE_DT_GET(DT_NODELABEL(i2c0));
	int ret;

	if (!device_is_ready(i2c_dev)) {
		printk("I2C device not ready\n");
		return -ENODEV;
	}

	/* Buffer: [register_addr, data0, data1, data2, data3] */
	uint8_t write_buf[1 + DATA_LEN] = {
		REG_ADDR,
		0x11, 0x22, 0x33, 0x44,
	};

	struct i2c_msg msgs[1] = {
		{
			.buf   = write_buf,
			.len   = sizeof(write_buf),
			.flags = I2C_MSG_WRITE | I2C_MSG_STOP,
		},
	};

	ret = i2c_transfer(i2c_dev, msgs, ARRAY_SIZE(msgs), DEV_ADDR);
	if (ret < 0) {
		printk("I2C register write failed: %d\n", ret);
		return ret;
	}

	printk("Register write OK\n");
	return 0;
}
