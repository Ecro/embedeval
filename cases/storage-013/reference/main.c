#include <zephyr/kernel.h>
#include <zephyr/settings/settings.h>
#include <zephyr/sys/printk.h>

#define SETTINGS_KEY           "sensor/counter"
#define TOTAL_ITER             500
#define SENSOR_PERIOD_MS       10
/* Flash-endurance guardrail: persist at most once per PERSIST_EVERY iterations.
 * 100 iterations * 10ms = 1 flash write per second. At 100k cycles this gives
 * ~27 hours of wear-free lifetime per page — combined with NVS wear-leveling
 * (multi-page rotation) this extends to years. */
#define PERSIST_EVERY          100

static uint32_t counter;

static int counter_load_cb(const char *key, size_t len,
			   settings_read_cb read_cb, void *cb_arg, void *param)
{
	ARG_UNUSED(key);
	ARG_UNUSED(param);

	if (len != sizeof(counter)) {
		return -EINVAL;
	}
	return read_cb(cb_arg, &counter, sizeof(counter));
}

static struct settings_handler counter_handler = {
	.name  = "sensor",
	.h_set = counter_load_cb,
};

static void persist_counter(void)
{
	(void)settings_save_one(SETTINGS_KEY, &counter, sizeof(counter));
}

int main(void)
{
	int ret = settings_subsys_init();

	if (ret < 0) {
		printk("settings init failed: %d\n", ret);
		return ret;
	}

	(void)settings_register(&counter_handler);
	(void)settings_load();

	for (uint32_t i = 0; i < TOTAL_ITER; i++) {
		counter++;

		/* Rate-limit flash writes: persist every PERSIST_EVERY iterations
		 * instead of every 10 ms. Without this rate limit a years-long
		 * deployment would burn through the flash page erase budget. */
		if ((counter % PERSIST_EVERY) == 0U) {
			persist_counter();
		}

		k_msleep(SENSOR_PERIOD_MS);
	}

	/* Final persist so the exact final value is recoverable. */
	persist_counter();

	printk("final counter=%u\n", counter);
	return 0;
}
