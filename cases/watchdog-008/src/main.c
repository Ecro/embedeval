#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/watchdog.h>

int main(void)
{
	const struct device *wdt = DEVICE_DT_GET(DT_ALIAS(watchdog0));

	if (!device_is_ready(wdt)) {
		printk("WDT not ready\n");
		return -1;
	}

	struct wdt_timeout_cfg wdt_cfg = {
		.flags = WDT_FLAG_RESET_SOC,
		.window.min = 0,
		.window.max = 2000,
		.callback = NULL,
	};

	int wdt_channel_id = wdt_install_timeout(wdt, &wdt_cfg);

	if (wdt_channel_id < 0) {
		printk("WDT install failed: %d\n", wdt_channel_id);
		return -1;
	}

	int err = wdt_setup(wdt, WDT_OPT_PAUSE_HALTED_BY_DBG);

	if (err < 0) {
		printk("WDT setup failed: %d\n", err);
		return -1;
	}

	for (int i = 0; i < 10; i++) {
		printk("Heartbeat %d — feeding WDT\n", i);
		wdt_feed(wdt, wdt_channel_id);
		k_sleep(K_SECONDS(1));
	}

	return 0;
}
