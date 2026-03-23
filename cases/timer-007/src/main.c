#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/watchdog.h>

static const struct device *wdt;
static int wdt_channel_id;

static void wdt_feed_timer_cb(struct k_timer *timer)
{
	wdt_feed(wdt, wdt_channel_id);
}

K_TIMER_DEFINE(wdt_feed_timer, wdt_feed_timer_cb, NULL);

int main(void)
{
	wdt = DEVICE_DT_GET(DT_ALIAS(watchdog0));

	if (!device_is_ready(wdt)) {
		printk("Watchdog not ready\n");
		return -1;
	}

	struct wdt_timeout_cfg wdt_cfg = {
		.flags = WDT_FLAG_RESET_SOC,
		.window.min = 0,
		.window.max = 3000,
		.callback = NULL,
	};

	wdt_channel_id = wdt_install_timeout(wdt, &wdt_cfg);
	if (wdt_channel_id < 0) {
		printk("WDT install failed: %d\n", wdt_channel_id);
		return -1;
	}

	int err = wdt_setup(wdt, WDT_OPT_PAUSE_HALTED_BY_DBG);

	if (err < 0) {
		printk("WDT setup failed: %d\n", err);
		return -1;
	}

	/* Timer period (1s) is shorter than WDT timeout (3s) */
	k_timer_start(&wdt_feed_timer, K_SECONDS(1), K_SECONDS(1));

	while (1) {
		printk("System heartbeat\n");
		k_sleep(K_SECONDS(5));
	}

	return 0;
}
