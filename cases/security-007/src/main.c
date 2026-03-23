#include <zephyr/kernel.h>
#include <zephyr/net/tls_credentials.h>

#define TLS_SEC_TAG 42

/* Placeholder PEM buffers — in production these come from secure storage */
static const char ca_cert[] =
	"-----BEGIN CERTIFICATE-----\n"
	"MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0placeholder==\n"
	"-----END CERTIFICATE-----\n";

static const char client_cert[] =
	"-----BEGIN CERTIFICATE-----\n"
	"MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1placeholder==\n"
	"-----END CERTIFICATE-----\n";

static const char client_key[] =
	"-----BEGIN PRIVATE KEY-----\n"
	"MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC2placeholder==\n"
	"-----END PRIVATE KEY-----\n";

int main(void)
{
	int ret;

	/* Load CA certificate (used to verify server) */
	ret = tls_credential_add(TLS_SEC_TAG,
				 TLS_CREDENTIAL_CA_CERTIFICATE,
				 ca_cert, sizeof(ca_cert));
	if (ret != 0) {
		printk("Failed to add CA cert: %d\n", ret);
		printk("TLS CREDS FAILED\n");
		return ret;
	}

	/* Load client certificate (sent to server for mutual auth) */
	ret = tls_credential_add(TLS_SEC_TAG,
				 TLS_CREDENTIAL_SERVER_CERTIFICATE,
				 client_cert, sizeof(client_cert));
	if (ret != 0) {
		printk("Failed to add client cert: %d\n", ret);
		printk("TLS CREDS FAILED\n");
		return ret;
	}

	/* Load client private key */
	ret = tls_credential_add(TLS_SEC_TAG,
				 TLS_CREDENTIAL_PRIVATE_KEY,
				 client_key, sizeof(client_key));
	if (ret != 0) {
		printk("Failed to add client key: %d\n", ret);
		printk("TLS CREDS FAILED\n");
		return ret;
	}

	printk("TLS CREDS OK\n");
	return 0;
}
