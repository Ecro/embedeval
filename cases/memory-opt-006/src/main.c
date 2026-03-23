CONFIG_THREAD_STACK_INFO=y
CONFIG_STACK_SENTINEL=y
CONFIG_STACK_USAGE=y

#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>

LOG_MODULE_REGISTER(stack_check, LOG_LEVEL_DBG);

#define CRITICAL_STACK_THRESHOLD 256U

void check_stack_headroom(size_t warn_threshold)
{
	size_t unused;
	int ret;

	ret = k_thread_stack_space_get(k_current_get(), &unused);
	if (ret < 0) {
		LOG_ERR("Failed to get stack info: %d", ret);
		return;
	}

	if (unused < warn_threshold) {
		LOG_WRN("Low stack headroom: %zu bytes remaining (threshold %zu)",
			unused, warn_threshold);
	} else {
		LOG_DBG("Stack headroom OK: %zu bytes remaining", unused);
	}

	if (unused < CRITICAL_STACK_THRESHOLD) {
		LOG_ERR("CRITICAL: stack nearly exhausted (%zu bytes)", unused);
	}
}

int main(void)
{
	LOG_INF("Starting stack overflow detection demo");

	check_stack_headroom(512U);

	/* Simulate some stack usage */
	volatile char local_buf[128];
	(void)local_buf;

	check_stack_headroom(512U);
	LOG_INF("Stack check complete");

	return 0;
}
