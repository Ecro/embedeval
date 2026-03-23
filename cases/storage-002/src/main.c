#include <zephyr/kernel.h>
#include <zephyr/settings/settings.h>

#define SETTINGS_KEY "app/mykey"

static uint32_t loaded_val;

static int mykey_load_cb(const char *key, size_t len,
			 settings_read_cb read_cb, void *cb_arg, void *param)
{
	if (len != sizeof(loaded_val)) {
		return -EINVAL;
	}
	return read_cb(cb_arg, &loaded_val, sizeof(loaded_val));
}

static struct settings_handler my_handler = {
	.name = "app",
	.h_set = mykey_load_cb,
};

int main(void)
{
	int ret;
	uint32_t save_val = 42U;

	ret = settings_subsys_init();
	if (ret < 0) {
		printk("settings_subsys_init failed: %d\n", ret);
		return ret;
	}

	ret = settings_register(&my_handler);
	if (ret < 0) {
		printk("settings_register failed: %d\n", ret);
		return ret;
	}

	ret = settings_save_one(SETTINGS_KEY, &save_val, sizeof(save_val));
	if (ret < 0) {
		printk("settings_save_one failed: %d\n", ret);
		return ret;
	}

	loaded_val = 0U;

	ret = settings_load();
	if (ret < 0) {
		printk("settings_load failed: %d\n", ret);
		return ret;
	}

	if (loaded_val == save_val) {
		printk("Settings verify OK: %u\n", loaded_val);
	} else {
		printk("Settings verify FAIL: saved %u, loaded %u\n",
		       save_val, loaded_val);
		return -EIO;
	}

	return 0;
}
