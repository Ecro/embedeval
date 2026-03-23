#include <zephyr/kernel.h>
#include <zephyr/net/websocket.h>
#include <zephyr/net/tls_credentials.h>
#include <zephyr/net/socket.h>
#include <string.h>

#define SERVER_HOST "ws.example.com"
#define SERVER_PORT 443
#define SERVER_PATH "/ws"
#define SEC_TAG     1

static const char ca_cert[] =
	"-----BEGIN CERTIFICATE-----\n"
	"MIIBplaceholderCertificateDataForCompilation\n"
	"-----END CERTIFICATE-----\n";

static uint8_t recv_buf[512];

int main(void)
{
	int tcp_sock;
	int ws_sock;
	int ret;
	struct sockaddr_in server_addr;
	sec_tag_t sec_tag_list[] = {SEC_TAG};
	uint32_t message_type;
	uint64_t remaining;

	/* Register TLS credential BEFORE creating socket */
	ret = tls_credential_add(SEC_TAG, TLS_CREDENTIAL_CA_CERTIFICATE,
				 ca_cert, sizeof(ca_cert));
	if (ret < 0) {
		printk("Failed to add TLS credential: %d\n", ret);
		return ret;
	}

	tcp_sock = zsock_socket(AF_INET, SOCK_STREAM, IPPROTO_TLS_1_2);
	if (tcp_sock < 0) {
		printk("Failed to create TLS socket: %d\n", tcp_sock);
		return tcp_sock;
	}

	ret = zsock_setsockopt(tcp_sock, SOL_TLS, TLS_SEC_TAG_LIST,
			       sec_tag_list, sizeof(sec_tag_list));
	if (ret < 0) {
		printk("Failed to set TLS_SEC_TAG_LIST: %d\n", ret);
		zsock_close(tcp_sock);
		return ret;
	}

	ret = zsock_setsockopt(tcp_sock, SOL_TLS, TLS_HOSTNAME,
			       SERVER_HOST, strlen(SERVER_HOST));
	if (ret < 0) {
		printk("Failed to set TLS_HOSTNAME: %d\n", ret);
		zsock_close(tcp_sock);
		return ret;
	}

	memset(&server_addr, 0, sizeof(server_addr));
	server_addr.sin_family = AF_INET;
	server_addr.sin_port = htons(SERVER_PORT);
	net_addr_pton(AF_INET, "93.184.216.34", &server_addr.sin_addr);

	ret = zsock_connect(tcp_sock, (struct sockaddr *)&server_addr,
			    sizeof(server_addr));
	if (ret < 0) {
		printk("TCP/TLS connect failed: %d\n", ret);
		zsock_close(tcp_sock);
		return ret;
	}

	struct websocket_request ws_req = {
		.host = SERVER_HOST,
		.url  = SERVER_PATH,
		.cb   = NULL,
		.tmp_buf = recv_buf,
		.tmp_buf_len = sizeof(recv_buf),
	};

	ws_sock = websocket_connect(tcp_sock, &ws_req, 3000, NULL);
	if (ws_sock < 0) {
		printk("WebSocket connect failed: %d\n", ws_sock);
		zsock_close(tcp_sock);
		return ws_sock;
	}

	printk("WebSocket connected\n");

	const char *msg = "hello websocket";

	ret = websocket_send_msg(ws_sock, (uint8_t *)msg, strlen(msg),
				 WEBSOCKET_OPCODE_DATA_TEXT, true, true,
				 K_MSEC(3000));
	if (ret < 0) {
		printk("WebSocket send failed: %d\n", ret);
	} else {
		printk("WebSocket sent %zu bytes\n", strlen(msg));
	}

	ret = websocket_recv_msg(ws_sock, recv_buf, sizeof(recv_buf),
				 &message_type, &remaining, K_MSEC(5000));
	if (ret > 0) {
		printk("WebSocket received %d bytes\n", ret);
	}

	websocket_disconnect(ws_sock);
	zsock_close(tcp_sock);
	return 0;
}
