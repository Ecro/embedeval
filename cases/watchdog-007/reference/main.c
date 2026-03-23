#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/watchdog.h>
#include <zephyr/sys/atomic.h>

static const struct device *wdt;
static int wdt_channel_id;

static atomic_t thread0_healthy;
static atomic_t thread1_healthy;
static atomic_t thread2_healthy;

static void worker0(void *p1, void *p2, void *p3)
{
	while (1) {
		printk("Worker 0 alive\n");
		k_sleep(K_SECONDS(1));
		atomic_set(&thread0_healthy, 1);
	}
}

static void worker1(void *p1, void *p2, void *p3)
{
	while (1) {
		printk("Worker 1 alive\n");
		k_sleep(K_SECONDS(1));
		atomic_set(&thread1_healthy, 1);
	}
}

static void worker2(void *p1, void *p2, void *p3)
{
	while (1) {
		printk("Worker 2 alive\n");
		k_sleep(K_SECONDS(1));
		atomic_set(&thread2_healthy, 1);
	}
}

static void supervisor(void *p1, void *p2, void *p3)
{
	while (1) {
		k_sleep(K_SECONDS(2));

		int h0 = atomic_get(&thread0_healthy);
		int h1 = atomic_get(&thread1_healthy);
		int h2 = atomic_get(&thread2_healthy);

		printk("Health: t0=%d t1=%d t2=%d\n", h0, h1, h2);

		if (h0 && h1 && h2) {
			atomic_clear(&thread0_healthy);
			atomic_clear(&thread1_healthy);
			atomic_clear(&thread2_healthy);
			wdt_feed(wdt, wdt_channel_id);
			printk("All healthy — WDT fed\n");
		} else {
			printk("Unhealthy thread detected — not feeding WDT\n");
		}
	}
}

K_THREAD_DEFINE(t0, 512, worker0, NULL, NULL, NULL, 5, 0, 0);
K_THREAD_DEFINE(t1, 512, worker1, NULL, NULL, NULL, 5, 0, 0);
K_THREAD_DEFINE(t2, 512, worker2, NULL, NULL, NULL, 5, 0, 0);
K_THREAD_DEFINE(tsup, 512, supervisor, NULL, NULL, NULL, 4, 0, 0);

int main(void)
{
	wdt = DEVICE_DT_GET(DT_ALIAS(watchdog0));

	if (!device_is_ready(wdt)) {
		printk("WDT not ready\n");
		return -1;
	}

	struct wdt_timeout_cfg wdt_cfg = {
		.flags = WDT_FLAG_RESET_SOC,
		.window.min = 0,
		.window.max = 5000,
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

	k_sleep(K_FOREVER);
	return 0;
}
