#include <zephyr/kernel.h>
#include <zephyr/net/socket.h>
#include <errno.h>
#include <string.h>

#define SERVER_ADDR  "192.168.1.100"
#define SERVER_PORT  8080
#define MAX_RETRIES  3

static int connect_with_retry(void)
{
	int sock;
	int ret;
	struct sockaddr_in server;
	int delay = 1;

	sock = zsock_socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
	if (sock < 0) {
		printk("Failed to create socket: %d\n", sock);
		return -1;
	}

	memset(&server, 0, sizeof(server));
	server.sin_family = AF_INET;
	server.sin_port = htons(SERVER_PORT);
	net_addr_pton(AF_INET, SERVER_ADDR, &server.sin_addr);

	for (int attempt = 1; attempt <= MAX_RETRIES; attempt++) {
		printk("Connection attempt %d/%d\n", attempt, MAX_RETRIES);

		ret = zsock_connect(sock, (struct sockaddr *)&server,
				    sizeof(server));
		if (ret == 0) {
			return sock;
		}

		printk("Connect failed (errno=%d), retrying in %ds\n",
		       errno, delay);

		if (attempt < MAX_RETRIES) {
			k_sleep(K_SECONDS(delay));
			delay *= 2;
		}
	}

	printk("All %d connection attempts failed\n", MAX_RETRIES);
	zsock_close(sock);
	return -1;
}

int main(void)
{
	int sock;
	int ret;
	const char *request = "GET / HTTP/1.0\r\n\r\n";

	sock = connect_with_retry();
	if (sock < 0) {
		printk("Failed to connect\n");
		return -1;
	}

	printk("Connected\n");

	ret = zsock_send(sock, request, strlen(request), 0);
	if (ret < 0) {
		printk("Send failed: %d\n", ret);
	} else {
		printk("Sent %d bytes\n", ret);
	}

	zsock_close(sock);
	return 0;
}
