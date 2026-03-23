#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/watchdog.h>

void wdt_callback(const struct device *wdt_dev, int channel_id)
{
	printk("WDT timeout! Resetting...\n");
}

int main(void)
{
	const struct device *const wdt = DEVICE_DT_GET(DT_ALIAS(watchdog0));
	int wdt_channel_id;

	if (!device_is_ready(wdt)) {
		printk("Watchdog device not ready\n");
		return -1;
	}

	struct wdt_timeout_cfg wdt_config = {
		.flags = WDT_FLAG_RESET_SOC,
		.window.min = 0,
		.window.max = 2000,
		.callback = wdt_callback,
	};

	wdt_channel_id = wdt_install_timeout(wdt, &wdt_config);
	if (wdt_channel_id < 0) {
		printk("Watchdog install failed: %d\n", wdt_channel_id);
		return -1;
	}

	int err = wdt_setup(wdt, WDT_OPT_PAUSE_HALTED_BY_DBG);

	if (err < 0) {
		printk("Watchdog setup failed: %d\n", err);
		return -1;
	}

	for (int i = 0; i < 5; i++) {
		printk("Heartbeat %d\n", i);
		wdt_feed(wdt, wdt_channel_id);
		k_sleep(K_SECONDS(1));
	}

	printk("Stopping feed - reset expected\n");

	while (1) {
		k_sleep(K_SECONDS(1));
	}

	return 0;
}
