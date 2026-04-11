#include <zephyr/kernel.h>
#include <psa/crypto.h>
#include <string.h>

#define SHA256_DIGEST_SIZE 32

static const uint8_t message[] = "Hello Zephyr";

/* SHA-256("Hello Zephyr") = 76c30c504ec4717d642f43cc2506b24fa15ae188c93250be85b54ee97b8d5fe6 */
static const uint8_t expected_hash[SHA256_DIGEST_SIZE] = {
	0x76, 0xc3, 0x0c, 0x50, 0x4e, 0xc4, 0x71, 0x7d,
	0x64, 0x2f, 0x43, 0xcc, 0x25, 0x06, 0xb2, 0x4f,
	0xa1, 0x5a, 0xe1, 0x88, 0xc9, 0x32, 0x50, 0xbe,
	0x85, 0xb5, 0x4e, 0xe9, 0x7b, 0x8d, 0x5f, 0xe6,
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
