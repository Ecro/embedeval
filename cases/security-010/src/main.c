#include <zephyr/kernel.h>
#include <psa/crypto.h>

/* P-256 public key in uncompressed form: 0x04 || X(32) || Y(32) = 65 bytes */
#define PUBLIC_KEY_SIZE PSA_EXPORT_PUBLIC_KEY_OUTPUT_SIZE( \
	PSA_KEY_TYPE_ECC_KEY_PAIR(PSA_ECC_FAMILY_SECP_R1), 256)

int main(void)
{
	psa_status_t status;
	psa_key_attributes_t attrs = PSA_KEY_ATTRIBUTES_INIT;
	psa_key_id_t key_id;
	uint8_t pub_key[PUBLIC_KEY_SIZE];
	size_t pub_key_len;
	uint8_t priv_export_buf[64];
	size_t priv_export_len;

	status = psa_crypto_init();
	if (status != PSA_SUCCESS) {
		printk("psa_crypto_init failed: %d\n", status);
		return -1;
	}

	psa_set_key_type(&attrs,
			 PSA_KEY_TYPE_ECC_KEY_PAIR(PSA_ECC_FAMILY_SECP_R1));
	psa_set_key_bits(&attrs, 256);
	psa_set_key_algorithm(&attrs, PSA_ALG_ECDSA(PSA_ALG_SHA_256));
	/* No PSA_KEY_USAGE_EXPORT — private key is non-extractable */
	psa_set_key_usage_flags(&attrs, PSA_KEY_USAGE_SIGN_HASH);

	status = psa_generate_key(&attrs, &key_id);
	if (status != PSA_SUCCESS) {
		printk("psa_generate_key failed: %d\n", status);
		return -1;
	}

	/* Export the PUBLIC key (allowed) */
	status = psa_export_public_key(key_id, pub_key, sizeof(pub_key),
				       &pub_key_len);
	if (status != PSA_SUCCESS) {
		printk("psa_export_public_key failed: %d\n", status);
		psa_destroy_key(key_id);
		return -1;
	}

	/* Verify PRIVATE key export is denied */
	status = psa_export_key(key_id, priv_export_buf,
				sizeof(priv_export_buf), &priv_export_len);
	if (status != PSA_ERROR_NOT_PERMITTED) {
		printk("WARNING: private key export not denied! status=%d\n",
		       status);
	}

	printk("ECDSA KEY OK: pubkey_len=%zu\n", pub_key_len);

	psa_destroy_key(key_id);
	return 0;
}
