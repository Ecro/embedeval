#include <zephyr/kernel.h>
#include <psa/crypto.h>
#include <string.h>

#define AES_KEY_SIZE 32
#define AES_BLOCK_SIZE 16

static const uint8_t aes_key[AES_KEY_SIZE] = {
	0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
	0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
	0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17,
	0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f,
};

static const uint8_t plaintext[AES_BLOCK_SIZE] = {
	'H', 'e', 'l', 'l', 'o', ' ', 'Z', 'e',
	'p', 'h', 'y', 'r', '!', 0x00, 0x00, 0x00,
};

int main(void)
{
	psa_status_t status;
	psa_key_id_t key_id;
	psa_key_attributes_t attributes = PSA_KEY_ATTRIBUTES_INIT;
	uint8_t ciphertext[AES_BLOCK_SIZE + AES_BLOCK_SIZE];
	uint8_t decrypted[AES_BLOCK_SIZE];
	size_t output_len;

	status = psa_crypto_init();
	if (status != PSA_SUCCESS) {
		printk("PSA crypto init failed: %d\n", status);
		return -1;
	}

	psa_set_key_type(&attributes, PSA_KEY_TYPE_AES);
	psa_set_key_bits(&attributes, 256);
	psa_set_key_algorithm(&attributes, PSA_ALG_CBC_NO_PADDING);
	psa_set_key_usage_flags(&attributes,
				PSA_KEY_USAGE_ENCRYPT | PSA_KEY_USAGE_DECRYPT);

	status = psa_import_key(&attributes, aes_key, sizeof(aes_key), &key_id);
	if (status != PSA_SUCCESS) {
		printk("Key import failed: %d\n", status);
		return -1;
	}

	status = psa_cipher_encrypt(key_id, PSA_ALG_CBC_NO_PADDING,
				     plaintext, sizeof(plaintext),
				     ciphertext, sizeof(ciphertext),
				     &output_len);
	if (status != PSA_SUCCESS) {
		printk("Encryption failed: %d\n", status);
		psa_destroy_key(key_id);
		return -1;
	}

	status = psa_cipher_decrypt(key_id, PSA_ALG_CBC_NO_PADDING,
				     ciphertext, output_len,
				     decrypted, sizeof(decrypted),
				     &output_len);
	if (status != PSA_SUCCESS) {
		printk("Decryption failed: %d\n", status);
		psa_destroy_key(key_id);
		return -1;
	}

	if (memcmp(plaintext, decrypted, sizeof(plaintext)) == 0) {
		printk("AES-256-CBC encrypt/decrypt OK\n");
	} else {
		printk("AES-256-CBC verify FAILED\n");
	}

	psa_destroy_key(key_id);
	return 0;
}
