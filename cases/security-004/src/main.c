#include <zephyr/kernel.h>
#include <psa/crypto.h>
#include <string.h>

#define DERIVED_KEY_SIZE 32

static const uint8_t password[] = "my-secret-password";
static const uint8_t salt[] = {
	0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
	0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x10,
};
static const uint8_t info[] = "key-derivation-v1";

int main(void)
{
	psa_status_t status;
	psa_key_derivation_operation_t op = PSA_KEY_DERIVATION_OPERATION_INIT;
	uint8_t derived_key[DERIVED_KEY_SIZE];

	status = psa_crypto_init();
	if (status != PSA_SUCCESS) {
		printk("PSA crypto init failed: %d\n", status);
		return -1;
	}

	status = psa_key_derivation_setup(&op, PSA_ALG_HKDF(PSA_ALG_SHA_256));
	if (status != PSA_SUCCESS) {
		printk("HKDF setup failed: %d\n", status);
		return -1;
	}

	status = psa_key_derivation_input_bytes(&op,
						PSA_KEY_DERIVATION_INPUT_SALT,
						salt, sizeof(salt));
	if (status != PSA_SUCCESS) {
		printk("HKDF salt input failed: %d\n", status);
		psa_key_derivation_abort(&op);
		return -1;
	}

	status = psa_key_derivation_input_bytes(&op,
						PSA_KEY_DERIVATION_INPUT_SECRET,
						password, sizeof(password) - 1);
	if (status != PSA_SUCCESS) {
		printk("HKDF secret input failed: %d\n", status);
		psa_key_derivation_abort(&op);
		return -1;
	}

	status = psa_key_derivation_input_bytes(&op,
						PSA_KEY_DERIVATION_INPUT_INFO,
						info, sizeof(info) - 1);
	if (status != PSA_SUCCESS) {
		printk("HKDF info input failed: %d\n", status);
		psa_key_derivation_abort(&op);
		return -1;
	}

	status = psa_key_derivation_output_bytes(&op, derived_key, sizeof(derived_key));
	if (status != PSA_SUCCESS) {
		printk("HKDF output failed: %d\n", status);
		psa_key_derivation_abort(&op);
		return -1;
	}

	psa_key_derivation_abort(&op);

	printk("Derived key[0..3]: %02x %02x %02x %02x\n",
	       derived_key[0], derived_key[1], derived_key[2], derived_key[3]);
	printk("HKDF OK\n");

	return 0;
}
