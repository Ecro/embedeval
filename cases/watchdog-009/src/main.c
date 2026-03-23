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

	/* Window: feed must happen between 500ms and 2000ms after last feed/setup */
	struct wdt_timeout_cfg wdt_cfg = {
		.flags = WDT_FLAG_RESET_SOC,
		.window.min = 500,
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

	while (1) {
		/* Wait at least window.min (500ms) but less than window.max (2000ms) */
		printk("Waiting in window...\n");
		k_sleep(K_MSEC(1000));

		printk("Feeding WDT within window [500ms, 2000ms]\n");
		wdt_feed(wdt, wdt_channel_id);
	}

	return 0;
}
