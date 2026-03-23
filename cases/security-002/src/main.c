#include <zephyr/kernel.h>
#include <psa/crypto.h>
#include <string.h>

#define SHA256_DIGEST_SIZE 32

static const uint8_t message[] = "Hello Zephyr";

/* SHA-256("Hello Zephyr") */
static const uint8_t expected_hash[SHA256_DIGEST_SIZE] = {
	0x42, 0x4e, 0x3d, 0x5b, 0x25, 0xc0, 0x9e, 0x6a,
	0x9f, 0x4c, 0xb0, 0x3a, 0x17, 0x8e, 0x2b, 0x44,
	0xd7, 0x91, 0xf9, 0x62, 0x3a, 0x5e, 0x1c, 0x07,
	0x8a, 0xf5, 0x62, 0x9e, 0xd0, 0xb3, 0x4f, 0x2a,
};

int main(void)
{
	psa_status_t status;
	uint8_t hash[SHA256_DIGEST_SIZE];
	size_t hash_len;

	status = psa_crypto_init();
	if (status != PSA_SUCCESS) {
		printk("PSA crypto init failed: %d\n", status);
		return -1;
	}

	status = psa_hash_compute(PSA_ALG_SHA_256,
				  message, sizeof(message) - 1,
				  hash, sizeof(hash),
				  &hash_len);
	if (status != PSA_SUCCESS) {
		printk("SHA-256 compute failed: %d\n", status);
		return -1;
	}

	if (hash_len != SHA256_DIGEST_SIZE) {
		printk("SHA-256 wrong digest length: %zu\n", hash_len);
		return -1;
	}

	if (memcmp(hash, expected_hash, SHA256_DIGEST_SIZE) == 0) {
		printk("SHA-256 OK\n");
	} else {
		printk("SHA-256 FAILED\n");
	}

	return 0;
}
