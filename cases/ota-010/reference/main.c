#include <zephyr/kernel.h>
#include <zephyr/dfu/mcuboot.h>
#include <zephyr/dfu/dfu_target.h>
#include <zephyr/sys/crc.h>
#include <string.h>
#include <errno.h>

#define SOURCE_SIZE  4096
#define PATCH_SIZE   512
#define TARGET_SIZE  4096

static uint8_t source_image[SOURCE_SIZE];
static uint8_t patch_data[PATCH_SIZE];
static uint8_t target_image[TARGET_SIZE];

static int verify_patch_integrity(const uint8_t *patch, size_t len,
				   uint32_t expected_crc)
{
	uint32_t computed = crc32_ieee(patch, len);

	if (computed != expected_crc) {
		printk("Patch CRC mismatch: got 0x%08x, expected 0x%08x\n",
		       computed, expected_crc);
		return -EBADMSG;
	}
	return 0;
}

static int apply_patch(const uint8_t *src, size_t src_len,
		       const uint8_t *patch, size_t patch_len,
		       uint8_t *target, size_t target_len)
{
	if (src_len > target_len) {
		return -EINVAL;
	}

	memcpy(target, src, src_len);

	for (size_t i = 0; i < patch_len; i++) {
		target[i % target_len] ^= patch[i];
	}

	return 0;
}

int main(void)
{
	int ret;
	uint32_t expected_patch_crc;

	printk("Delta OTA patch application demo\n");

	/* Simulate known image and patch data */
	memset(source_image, 0x5A, SOURCE_SIZE);
	memset(patch_data, 0x01, PATCH_SIZE);

	/* Compute expected CRC (simulates pre-distribution CRC embedded in manifest) */
	expected_patch_crc = crc32_ieee(patch_data, PATCH_SIZE);

	/* Step 1: Verify patch integrity BEFORE applying */
	ret = verify_patch_integrity(patch_data, PATCH_SIZE, expected_patch_crc);
	if (ret < 0) {
		printk("Patch integrity check failed — aborting\n");
		return ret;
	}

	printk("Patch integrity verified OK\n");

	/* Step 2: Apply patch: source + patch -> target */
	ret = apply_patch(source_image, SOURCE_SIZE,
			  patch_data, PATCH_SIZE,
			  target_image, TARGET_SIZE);
	if (ret < 0) {
		printk("apply_patch failed: %d\n", ret);
		return ret;
	}

	printk("Patch applied successfully\n");

	/* Step 3: Write patched target image to flash */
	ret = dfu_target_init(DFU_TARGET_IMAGE_TYPE_MCUBOOT, 0, TARGET_SIZE, NULL);
	if (ret < 0) {
		printk("dfu_target_init failed: %d\n", ret);
		return ret;
	}

	ret = dfu_target_write(target_image, TARGET_SIZE);
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

	printk("Delta OTA complete\n");
	k_sleep(K_FOREVER);
	return 0;
}
