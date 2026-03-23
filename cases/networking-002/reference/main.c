#include <zephyr/kernel.h>
#include <zephyr/net/socket.h>
#include <string.h>

#define SERVER_ADDR "192.168.1.100"
#define SERVER_PORT 4242

int main(void)
{
	int sock;
	int ret;
	struct sockaddr_in server;
	char rx_buf[256];
	socklen_t addrlen = sizeof(server);

	sock = zsock_socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
	if (sock < 0) {
		printk("Failed to create socket: %d\n", sock);
		return sock;
	}

	memset(&server, 0, sizeof(server));
	server.sin_family = AF_INET;
	server.sin_port = htons(SERVER_PORT);
	net_addr_pton(AF_INET, SERVER_ADDR, &server.sin_addr);

	const char *msg = "hello";

	ret = zsock_sendto(sock, msg, strlen(msg), 0,
			   (struct sockaddr *)&server, sizeof(server));
	if (ret < 0) {
		printk("Failed to send: %d\n", ret);
		zsock_close(sock);
		return ret;
	}

	printk("Sent %d bytes\n", ret);

	ret = zsock_recvfrom(sock, rx_buf, sizeof(rx_buf) - 1, 0,
			     (struct sockaddr *)&server, &addrlen);
	if (ret < 0) {
		printk("Failed to receive: %d\n", ret);
		zsock_close(sock);
		return ret;
	}

	rx_buf[ret] = '\0';
	printk("Received %d bytes: %s\n", ret, rx_buf);

	zsock_close(sock);
	return 0;
}
