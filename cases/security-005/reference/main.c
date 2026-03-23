#include <zephyr/kernel.h>
#include <psa/crypto.h>
#include <psa/protected_storage.h>
#include <string.h>

#define SECRET_UID  42U
#define SECRET_SIZE 10

static const uint8_t secret[SECRET_SIZE] = "TopSecret";

int main(void)
{
	psa_status_t status;
	uint8_t retrieved[SECRET_SIZE];
	size_t actual_length;

	status = psa_crypto_init();
	if (status != PSA_SUCCESS) {
		printk("PSA crypto init failed: %d\n", status);
		return -1;
	}

	status = psa_ps_set(SECRET_UID, sizeof(secret), secret,
			    PSA_STORAGE_FLAG_NONE);
	if (status != PSA_SUCCESS) {
		printk("psa_ps_set failed: %d\n", status);
		return -1;
	}

	status = psa_ps_get(SECRET_UID, 0, sizeof(retrieved),
			    retrieved, &actual_length);
	if (status != PSA_SUCCESS) {
		printk("psa_ps_get failed: %d\n", status);
		return -1;
	}

	if (actual_length != sizeof(secret)) {
		printk("PS FAILED: length mismatch %zu != %zu\n",
		       actual_length, sizeof(secret));
		return -1;
	}

	if (memcmp(secret, retrieved, sizeof(secret)) == 0) {
		printk("PS OK\n");
	} else {
		printk("PS FAILED\n");
	}

	return 0;
}
