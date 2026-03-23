#include <zephyr/kernel.h>
#include <zephyr/net/http/client.h>
#include <zephyr/net/tls_credentials.h>
#include <zephyr/net/socket.h>
#include <string.h>

#define SERVER_HOST  "example.com"
#define SERVER_PORT  443
#define SERVER_PATH  "/"
#define SEC_TAG      1

static const char ca_certificate[] =
	"-----BEGIN CERTIFICATE-----\n"
	"MIIBplaceholder certificate data for compilation\n"
	"-----END CERTIFICATE-----\n";

static void response_cb(struct http_response *rsp,
			enum http_final_call final_data,
			void *user_data)
{
	if (rsp->data_len > 0) {
		printk("Received %zu bytes\n", rsp->data_len);
	}

	if (final_data == HTTP_DATA_FINAL) {
		printk("HTTP response complete, status: %u\n",
		       rsp->http_status_code);
	}
}

int main(void)
{
	int sock;
	int ret;
	struct sockaddr_in server;
	sec_tag_t sec_tag_list[] = {SEC_TAG};
	uint8_t recv_buf[512];

	ret = tls_credential_add(SEC_TAG, TLS_CREDENTIAL_CA_CERTIFICATE,
				 ca_certificate, sizeof(ca_certificate));
	if (ret < 0) {
		printk("Failed to add TLS credential: %d\n", ret);
		return ret;
	}

	sock = zsock_socket(AF_INET, SOCK_STREAM, IPPROTO_TLS_1_2);
	if (sock < 0) {
		printk("Failed to create TLS socket: %d\n", sock);
		return sock;
	}

	ret = zsock_setsockopt(sock, SOL_TLS, TLS_SEC_TAG_LIST,
			       sec_tag_list, sizeof(sec_tag_list));
	if (ret < 0) {
		printk("Failed to set TLS_SEC_TAG_LIST: %d\n", ret);
		zsock_close(sock);
		return ret;
	}

	ret = zsock_setsockopt(sock, SOL_TLS, TLS_HOSTNAME,
			       SERVER_HOST, strlen(SERVER_HOST));
	if (ret < 0) {
		printk("Failed to set TLS_HOSTNAME: %d\n", ret);
		zsock_close(sock);
		return ret;
	}

	memset(&server, 0, sizeof(server));
	server.sin_family = AF_INET;
	server.sin_port = htons(SERVER_PORT);
	net_addr_pton(AF_INET, "93.184.216.34", &server.sin_addr);

	ret = zsock_connect(sock, (struct sockaddr *)&server, sizeof(server));
	if (ret < 0) {
		printk("TLS connect failed: %d\n", ret);
		zsock_close(sock);
		return ret;
	}

	struct http_request req = {
		.method = HTTP_GET,
		.url = SERVER_PATH,
		.host = SERVER_HOST,
		.protocol = "HTTP/1.1",
		.response = response_cb,
		.recv_buf = recv_buf,
		.recv_buf_len = sizeof(recv_buf),
	};

	ret = http_client_req(sock, &req, 5000, NULL);
	if (ret < 0) {
		printk("HTTP request failed: %d\n", ret);
	} else {
		printk("HTTP request sent\n");
	}

	zsock_close(sock);
	return 0;
}
