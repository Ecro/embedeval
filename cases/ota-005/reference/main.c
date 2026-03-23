#include <zephyr/kernel.h>
#include <zephyr/dfu/mcuboot.h>
#include <zephyr/dfu/dfu_target.h>
#include <zephyr/sys/reboot.h>

#define CONFIRM_TIMEOUT_MS  30000
#define CHUNK_SIZE          256
#define TOTAL_SIZE          4096
#define NUM_CHUNKS          (TOTAL_SIZE / CHUNK_SIZE)

typedef enum {
	OTA_IDLE,
	OTA_DOWNLOADING,
	OTA_VERIFYING,
	OTA_REBOOTING,
	OTA_CONFIRMING,
} ota_state_t;

static uint8_t chunk[CHUNK_SIZE];

static int self_test(void)
{
	printk("Running self-test...\n");
	/* Real application: verify peripherals, connectivity, configuration */
	return 0;
}

static const char *state_name(ota_state_t state)
{
	switch (state) {
	case OTA_IDLE:        return "IDLE";
	case OTA_DOWNLOADING: return "DOWNLOADING";
	case OTA_VERIFYING:   return "VERIFYING";
	case OTA_REBOOTING:   return "REBOOTING";
	case OTA_CONFIRMING:  return "CONFIRMING";
	default:              return "UNKNOWN";
	}
}

static int ota_do_download(ota_state_t *state)
{
	int ret;
	int i;

	ret = dfu_target_init(DFU_TARGET_IMAGE_TYPE_MCUBOOT, 0, TOTAL_SIZE, NULL);
	if (ret < 0) {
		printk("dfu_target_init failed: %d\n", ret);
		return ret;
	}

	for (i = 0; i < NUM_CHUNKS; i++) {
		ret = dfu_target_write(chunk, sizeof(chunk));
		if (ret < 0) {
			printk("dfu_target_write failed at chunk %d: %d\n", i + 1, ret);
			dfu_target_done(false);
			return ret;
		}
	}

	*state = OTA_VERIFYING;
	return 0;
}

static int ota_do_verify(ota_state_t *state)
{
	int ret;

	ret = dfu_target_done(true);
	if (ret < 0) {
		printk("dfu_target_done failed: %d\n", ret);
		dfu_target_done(false);
		return ret;
	}

	*state = OTA_REBOOTING;
	return 0;
}

static int ota_do_reboot(ota_state_t *state)
{
	printk("Rebooting to test new image\n");
	*state = OTA_CONFIRMING;
	sys_reboot(SYS_REBOOT_COLD);
	return 0; /* unreachable */
}

static int ota_do_confirm(ota_state_t *state)
{
	int ret;
	int64_t deadline = k_uptime_get() + CONFIRM_TIMEOUT_MS;

	if (boot_is_img_confirmed()) {
		printk("Image already confirmed\n");
		*state = OTA_IDLE;
		return 0;
	}

	ret = self_test();
	if (ret != 0) {
		printk("Self-test failed (%d) — not confirming, rollback will occur\n", ret);
		return ret;
	}

	if (k_uptime_get() > deadline) {
		printk("Confirm timeout — not confirming, rollback will occur\n");
		return -ETIMEDOUT;
	}

	ret = boot_write_img_confirmed();
	if (ret < 0) {
		printk("boot_write_img_confirmed failed: %d\n", ret);
		return ret;
	}

	printk("Image confirmed successfully\n");
	*state = OTA_IDLE;
	return 0;
}

int main(void)
{
	ota_state_t state = OTA_DOWNLOADING;
	int ret;

	/* After a reboot from OTA_REBOOTING, pick up at CONFIRMING */
	if (!boot_is_img_confirmed()) {
		printk("Unconfirmed image detected — entering CONFIRMING state\n");
		state = OTA_CONFIRMING;
	}

	while (1) {
		printk("OTA state: %s\n", state_name(state));

		switch (state) {
		case OTA_IDLE:
			k_sleep(K_FOREVER);
			break;
		case OTA_DOWNLOADING:
			ret = ota_do_download(&state);
			if (ret < 0) {
				printk("Download failed, returning to IDLE\n");
				state = OTA_IDLE;
			}
			break;
		case OTA_VERIFYING:
			ret = ota_do_verify(&state);
			if (ret < 0) {
				printk("Verify failed, returning to IDLE\n");
				state = OTA_IDLE;
			}
			break;
		case OTA_REBOOTING:
			ota_do_reboot(&state);
			break;
		case OTA_CONFIRMING:
			ret = ota_do_confirm(&state);
			if (ret < 0) {
				printk("Confirmation failed — MCUboot will rollback\n");
				state = OTA_IDLE;
			}
			break;
		default:
			printk("Unknown state %d\n", state);
			state = OTA_IDLE;
			break;
		}
	}

	return 0;
}
