#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/i2c.h>

#define TARGET_ADDR 0x55

static uint8_t received_byte;
static uint8_t send_byte = 0xAB;

static int target_write_requested(struct i2c_target_config *config)
{
	return 0;
}

static int target_read_requested(struct i2c_target_config *config, uint8_t *val)
{
	*val = send_byte;
	return 0;
}

static int target_write_received(struct i2c_target_config *config, uint8_t val)
{
	received_byte = val;
	return 0;
}

static int target_read_processed(struct i2c_target_config *config, uint8_t *val)
{
	send_byte++;
	*val = send_byte;
	return 0;
}

static const struct i2c_target_callbacks target_callbacks = {
	.write_requested = target_write_requested,
	.read_requested  = target_read_requested,
	.write_received  = target_write_received,
	.read_processed  = target_read_processed,
};

static struct i2c_target_config target_cfg = {
	.address   = TARGET_ADDR,
	.callbacks = &target_callbacks,
};

int main(void)
{
	const struct device *const i2c_dev = DEVICE_DT_GET(DT_NODELABEL(i2c0));
	int ret;

	if (!device_is_ready(i2c_dev)) {
		printk("I2C device not ready\n");
		return -ENODEV;
	}

	ret = i2c_target_register(i2c_dev, &target_cfg);
	if (ret < 0) {
		printk("I2C target register failed: %d\n", ret);
		return ret;
	}

	printk("I2C target registered at 0x%02x\n", TARGET_ADDR);

	k_sleep(K_FOREVER);

	return 0;
}
