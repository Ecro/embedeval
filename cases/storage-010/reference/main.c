#include <zephyr/kernel.h>
#include <zephyr/settings/settings.h>

#define DEFAULT_VALUE  42U
#define SETTINGS_KEY   "app/value"

static uint32_t app_value = DEFAULT_VALUE;
static bool setting_loaded;

static int app_settings_set(const char *key, size_t len,
			    settings_read_cb read_cb, void *cb_arg)
{
	if (strcmp(key, "value") == 0) {
		if (len != sizeof(app_value)) {
			return -EINVAL;
		}
		int rc = read_cb(cb_arg, &app_value, sizeof(app_value));

		if (rc >= 0) {
			setting_loaded = true;
		}
		return rc;
	}
	return -ENOENT;
}

SETTINGS_STATIC_HANDLER_DEFINE(app, "app", NULL, app_settings_set, NULL, NULL);

int main(void)
{
	int ret;

	ret = settings_subsys_init();
	if (ret < 0) {
		printk("settings_subsys_init failed: %d\n", ret);
		return ret;
	}

	ret = settings_load();
	if (ret < 0) {
		printk("settings_load failed: %d\n", ret);
		return ret;
	}

	if (setting_loaded) {
		printk("SETTING=%u (loaded)\n", app_value);
	} else {
		/* First boot: key not in storage — use default */
		app_value = DEFAULT_VALUE;
		printk("SETTING=%u (default)\n", app_value);
	}

	return 0;
}
