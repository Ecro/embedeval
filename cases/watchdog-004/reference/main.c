#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/watchdog.h>

int main(void)
{
	const struct device *const wdt = DEVICE_DT_GET(DT_ALIAS(watchdog0));
	int ch0_id, ch1_id;

	if (!device_is_ready(wdt)) {
		printk("Watchdog device not ready\n");
		return -1;
	}

	struct wdt_timeout_cfg ch0_config = {
		.flags = WDT_FLAG_RESET_SOC,
		.window.min = 0,
		.window.max = 1000,
		.callback = NULL,
	};

	ch0_id = wdt_install_timeout(wdt, &ch0_config);
	if (ch0_id < 0) {
		printk("Channel 0 install failed: %d\n", ch0_id);
		return -1;
	}

	struct wdt_timeout_cfg ch1_config = {
		.flags = WDT_FLAG_RESET_SOC,
		.window.min = 0,
		.window.max = 5000,
		.callback = NULL,
	};

	ch1_id = wdt_install_timeout(wdt, &ch1_config);
	if (ch1_id < 0) {
		printk("Channel 1 install failed: %d\n", ch1_id);
		return -1;
	}

	int err = wdt_setup(wdt, WDT_OPT_PAUSE_HALTED_BY_DBG);

	if (err < 0) {
		printk("Watchdog setup failed: %d\n", err);
		return -1;
	}

	int iteration = 0;

	while (1) {
		printk("Feeding channel 0\n");
		wdt_feed(wdt, ch0_id);

		if (iteration % 8 == 0) {
			printk("Feeding channel 1\n");
			wdt_feed(wdt, ch1_id);
		}

		iteration++;
		k_sleep(K_MSEC(500));
	}

	return 0;
}
