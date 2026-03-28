#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/watchdog.h>
#include <zephyr/fs/nvs.h>
#include <zephyr/storage/flash_map.h>

#define WDT_TIMEOUT_MS      2000
#define WDT_FEED_INTERVAL_MS 1000
#define STABILITY_PERIOD_MS  30000
#define REBOOT_THRESHOLD     3

#define NVS_PARTITION        storage_partition
#define NVS_PARTITION_DEVICE FIXED_PARTITION_DEVICE(NVS_PARTITION)
#define NVS_PARTITION_OFFSET FIXED_PARTITION_OFFSET(NVS_PARTITION)

#define REBOOT_COUNT_ID      1

static struct nvs_fs nvs;
static int wdt_channel_id;

static int nvs_init_storage(void)
{
	int ret;

	nvs.flash_device = NVS_PARTITION_DEVICE;
	if (!device_is_ready(nvs.flash_device)) {
		printk("Flash device not ready\n");
		return -ENODEV;
	}

	nvs.offset = NVS_PARTITION_OFFSET;
	nvs.sector_size = 4096;
	nvs.sector_count = 2;

	ret = nvs_mount(&nvs);
	if (ret < 0) {
		printk("NVS mount failed: %d\n", ret);
		return ret;
	}

	return 0;
}

static int read_reboot_count(uint32_t *count)
{
	int ret;

	ret = nvs_read(&nvs, REBOOT_COUNT_ID, count, sizeof(*count));
	if (ret <= 0) {
		/* No entry or error — start from 0 */
		*count = 0;
	}

	return 0;
}

static int write_reboot_count(uint32_t count)
{
	int ret;

	ret = nvs_write(&nvs, REBOOT_COUNT_ID, &count, sizeof(count));
	if (ret < 0) {
		printk("NVS write failed: %d\n", ret);
		return ret;
	}

	return 0;
}

static int setup_watchdog(const struct device *wdt_dev)
{
	int ret;
	struct wdt_timeout_cfg wdt_cfg = {
		.window = {
			.min = 0,
			.max = WDT_TIMEOUT_MS,
		},
		.callback = NULL,
		.flags = WDT_FLAG_RESET_SOC,
	};

	wdt_channel_id = wdt_install_timeout(wdt_dev, &wdt_cfg);
	if (wdt_channel_id < 0) {
		printk("WDT install timeout failed: %d\n", wdt_channel_id);
		return wdt_channel_id;
	}

	ret = wdt_setup(wdt_dev, WDT_OPT_PAUSE_HALTED_BY_DBG);
	if (ret < 0) {
		printk("WDT setup failed: %d\n", ret);
		return ret;
	}

	return 0;
}

static void run_recovery_mode(const struct device *wdt_dev)
{
	printk("*** RECOVERY MODE ***\n");
	printk("System has rebooted %d+ times — entering safe mode\n",
	       REBOOT_THRESHOLD);

	/* In recovery mode: just feed the watchdog, do minimal work */
	/* Reset the counter so next boot can try normal mode again */
	uint32_t count = 0;

	write_reboot_count(count);
	printk("Reboot counter reset to 0 in recovery mode\n");

	while (1) {
		printk("Recovery mode heartbeat\n");
		wdt_feed(wdt_dev, wdt_channel_id);
		k_sleep(K_MSEC(WDT_FEED_INTERVAL_MS));
	}
}

static void run_normal_mode(const struct device *wdt_dev)
{
	int64_t start_time = k_uptime_get();
	bool counter_cleared = false;

	printk("*** NORMAL MODE ***\n");
	printk("Will clear reboot counter after %d ms of stable operation\n",
	       STABILITY_PERIOD_MS);

	while (1) {
		wdt_feed(wdt_dev, wdt_channel_id);

		/* Check if we have been stable long enough to clear counter */
		if (!counter_cleared &&
		    (k_uptime_get() - start_time) >= STABILITY_PERIOD_MS) {
			uint32_t count = 0;

			write_reboot_count(count);
			counter_cleared = true;
			printk("Stable for %d ms — reboot counter reset to 0\n",
			       STABILITY_PERIOD_MS);
		}

		printk("Normal mode heartbeat\n");
		k_sleep(K_MSEC(WDT_FEED_INTERVAL_MS));
	}
}

int main(void)
{
	const struct device *const wdt_dev = DEVICE_DT_GET(DT_ALIAS(watchdog0));
	uint32_t reboot_count;
	int ret;

	if (!device_is_ready(wdt_dev)) {
		printk("Watchdog device not ready\n");
		return -ENODEV;
	}

	/* Step 1: Initialize NVS and read reboot counter */
	ret = nvs_init_storage();
	if (ret < 0) {
		return ret;
	}

	ret = read_reboot_count(&reboot_count);
	if (ret < 0) {
		return ret;
	}

	printk("Boot count: %u (threshold: %d)\n", reboot_count, REBOOT_THRESHOLD);

	/* Step 2: Check if we should enter recovery mode */
	if (reboot_count >= REBOOT_THRESHOLD) {
		/* Set up watchdog even in recovery mode */
		ret = setup_watchdog(wdt_dev);
		if (ret < 0) {
			return ret;
		}
		run_recovery_mode(wdt_dev);
		/* Never returns */
	}

	/* Step 3: Increment and save counter before normal operation */
	reboot_count++;
	ret = write_reboot_count(reboot_count);
	if (ret < 0) {
		printk("Failed to save reboot count\n");
		return ret;
	}
	printk("Reboot counter incremented to %u\n", reboot_count);

	/* Step 4: Set up watchdog */
	ret = setup_watchdog(wdt_dev);
	if (ret < 0) {
		return ret;
	}

	/* Step 5: Run normal mode with periodic watchdog feed */
	run_normal_mode(wdt_dev);

	return 0;
}
