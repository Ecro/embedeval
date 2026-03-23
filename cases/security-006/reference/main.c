#include <zephyr/kernel.h>
#include <psa/crypto.h>

#define KEY_ID      1U
#define KEY_BITS    128

static const uint8_t key_material[16] = {
	0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
	0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
};

int main(void)
{
	psa_status_t status;
	psa_key_attributes_t attrs = PSA_KEY_ATTRIBUTES_INIT;
	psa_key_id_t key_id;
	uint8_t export_buf[16];
	size_t export_len;

	status = psa_crypto_init();
	if (status != PSA_SUCCESS) {
		printk("psa_crypto_init failed: %d\n", status);
		return -1;
	}

	psa_set_key_type(&attrs, PSA_KEY_TYPE_AES);
	psa_set_key_bits(&attrs, KEY_BITS);
	psa_set_key_algorithm(&attrs, PSA_ALG_CBC_NO_PADDING);
	psa_set_key_lifetime(&attrs, PSA_KEY_LIFETIME_PERSISTENT);
	psa_set_key_id(&attrs, KEY_ID);
	/* Intentionally NO PSA_KEY_USAGE_EXPORT — key is non-extractable */
	psa_set_key_usage_flags(&attrs, PSA_KEY_USAGE_ENCRYPT);

	status = psa_import_key(&attrs, key_material, sizeof(key_material),
				&key_id);
	if (status != PSA_SUCCESS) {
		printk("psa_import_key failed: %d\n", status);
		return -1;
	}

	/* Verify: export must be denied */
	status = psa_export_key(key_id, export_buf, sizeof(export_buf),
				&export_len);
	if (status == PSA_ERROR_NOT_PERMITTED) {
		printk("KEY SECURE\n");
	} else {
		printk("KEY EXPOSED\n");
	}

	psa_destroy_key(key_id);
	return 0;
}
