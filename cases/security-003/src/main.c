#include <zephyr/kernel.h>
#include <psa/crypto.h>
#include <string.h>

#define RNG_BUF_SIZE 32

int main(void)
{
	psa_status_t status;
	uint8_t buf[RNG_BUF_SIZE];
	int nonzero_count = 0;

	memset(buf, 0, sizeof(buf));

	status = psa_crypto_init();
	if (status != PSA_SUCCESS) {
		printk("PSA crypto init failed: %d\n", status);
		return -1;
	}

	status = psa_generate_random(buf, sizeof(buf));
	if (status != PSA_SUCCESS) {
		printk("psa_generate_random failed: %d\n", status);
		return -1;
	}

	for (int i = 0; i < RNG_BUF_SIZE; i++) {
		if (buf[i] != 0) {
			nonzero_count++;
		}
	}

	printk("Non-zero bytes: %d\n", nonzero_count);

	if (nonzero_count > 0) {
		printk("RNG OK\n");
	} else {
		printk("RNG FAILED\n");
	}

	return 0;
}
