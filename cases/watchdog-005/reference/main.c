#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/watchdog.h>

static volatile int worker_alive;

K_THREAD_STACK_DEFINE(worker_stack, 512);
static struct k_thread worker_thread;

void worker_fn(void *p1, void *p2, void *p3)
{
	while (1) {
		worker_alive = 1;
		printk("Worker alive\n");
		k_sleep(K_MSEC(500));
	}
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
		.window.max = 3000,
		.callback = NULL,
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

	k_thread_create(&worker_thread, worker_stack,
			K_THREAD_STACK_SIZEOF(worker_stack),
			worker_fn, NULL, NULL, NULL,
			5, 0, K_NO_WAIT);

	while (1) {
		k_sleep(K_SECONDS(1));

		if (worker_alive) {
			worker_alive = 0;
			printk("Feeding WDT\n");
			wdt_feed(wdt, wdt_channel_id);
		} else {
			printk("Worker stalled! Not feeding WDT\n");
		}
	}

	return 0;
}
