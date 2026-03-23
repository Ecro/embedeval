#include <zephyr/kernel.h>
#include <zephyr/dfu/mcuboot.h>
#include <zephyr/dfu/dfu_target.h>
#include <psa/crypto.h>
#include <string.h>
#include <errno.h>

#define IMAGE_SIZE  4096

static uint8_t image_buf[IMAGE_SIZE];

/* Pre-known SHA-256 hash of the expected image (32 bytes) */
static const uint8_t expected_hash[32] = {
	0xde, 0xad, 0xbe, 0xef, 0x01, 0x02, 0x03, 0x04,
	0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c,
	0x0d, 0x0e, 0x0f, 0x10, 0x11, 0x12, 0x13, 0x14,
	0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c,
};

static int compute_hash(const uint8_t *data, size_t len, uint8_t *out_hash)
{
	psa_status_t status;
	size_t hash_len = 0;

	status = psa_hash_compute(PSA_ALG_SHA_256, data, len,
				  out_hash, 32, &hash_len);
	if (status != PSA_SUCCESS) {
		printk("psa_hash_compute failed: %d\n", (int)status);
		return -EIO;
	}

	return 0;
}

static int verify_hash(const uint8_t *computed, const uint8_t *expected)
{
	if (memcmp(computed, expected, 32) != 0) {
		printk("Hash mismatch — aborting OTA\n");
		return -EBADMSG;
	}
	return 0;
}

int main(void)
{
	int ret;
	uint8_t computed_hash[32];

	printk("OTA hash verification demo\n");

	/* Step 1: Simulate download — populate image_buf */
	memset(image_buf, 0xAB, IMAGE_SIZE);

	/* Step 2: Compute hash BEFORE any flash write */
	ret = compute_hash(image_buf, IMAGE_SIZE, computed_hash);
	if (ret < 0) {
		printk("Hash computation failed: %d\n", ret);
		return ret;
	}

	/* Step 3: Verify hash against known-good value */
	ret = verify_hash(computed_hash, expected_hash);
	if (ret < 0) {
		printk("Hash verification failed — not writing to flash\n");
		return ret;
	}

	printk("Hash verified OK — proceeding with flash write\n");

	/* Step 4: Only now write to flash */
	ret = dfu_target_init(DFU_TARGET_IMAGE_TYPE_MCUBOOT, 0, IMAGE_SIZE, NULL);
	if (ret < 0) {
		printk("dfu_target_init failed: %d\n", ret);
		return ret;
	}

	ret = dfu_target_write(image_buf, IMAGE_SIZE);
	if (ret < 0) {
		printk("dfu_target_write failed: %d\n", ret);
		dfu_target_done(false);
		return ret;
	}

	ret = dfu_target_done(true);
	if (ret < 0) {
		printk("dfu_target_done failed: %d\n", ret);
		return ret;
	}

	printk("OTA image written successfully\n");
	k_sleep(K_FOREVER);
	return 0;
}
