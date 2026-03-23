#include <zephyr/kernel.h>
#include <psa/crypto.h>

static const uint8_t hmac_key[32] = {
	0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
	0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x10,
	0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18,
	0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f, 0x20,
};

static const uint8_t message[] = "Authenticate this message";

int main(void)
{
	psa_status_t status;
	psa_key_attributes_t attrs = PSA_KEY_ATTRIBUTES_INIT;
	psa_key_id_t key_id;
	psa_mac_operation_t operation = PSA_MAC_OPERATION_INIT;
	uint8_t mac[PSA_MAC_MAX_SIZE];
	size_t mac_len;

	status = psa_crypto_init();
	if (status != PSA_SUCCESS) {
		printk("psa_crypto_init failed: %d\n", status);
		return -1;
	}

	psa_set_key_type(&attrs, PSA_KEY_TYPE_HMAC);
	psa_set_key_bits(&attrs, 256);
	psa_set_key_algorithm(&attrs, PSA_ALG_HMAC(PSA_ALG_SHA_256));
	psa_set_key_usage_flags(&attrs, PSA_KEY_USAGE_SIGN_MESSAGE);

	status = psa_import_key(&attrs, hmac_key, sizeof(hmac_key), &key_id);
	if (status != PSA_SUCCESS) {
		printk("psa_import_key failed: %d\n", status);
		return -1;
	}

	status = psa_mac_sign_setup(&operation, key_id,
				    PSA_ALG_HMAC(PSA_ALG_SHA_256));
	if (status != PSA_SUCCESS) {
		printk("psa_mac_sign_setup failed: %d\n", status);
		psa_destroy_key(key_id);
		return -1;
	}

	status = psa_mac_update(&operation, message, sizeof(message) - 1);
	if (status != PSA_SUCCESS) {
		printk("psa_mac_update failed: %d\n", status);
		psa_mac_abort(&operation);
		psa_destroy_key(key_id);
		return -1;
	}

	status = psa_mac_sign_finish(&operation, mac, sizeof(mac), &mac_len);
	if (status != PSA_SUCCESS) {
		printk("psa_mac_sign_finish failed: %d\n", status);
		psa_mac_abort(&operation);
		psa_destroy_key(key_id);
		return -1;
	}

	printk("HMAC OK: %02x%02x%02x%02x...\n",
	       mac[0], mac[1], mac[2], mac[3]);

	psa_destroy_key(key_id);
	return 0;
}
