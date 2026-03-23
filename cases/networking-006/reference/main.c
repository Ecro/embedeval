#include <zephyr/kernel.h>
#include <zephyr/net/socket.h>
#include <string.h>
#include <stdio.h>

#define SERVER_PORT   4242
#define RECV_BUF_SIZE 256

static uint8_t recv_buf[RECV_BUF_SIZE];

int main(void)
{
	int serv_sock;
	int client_sock;
	int ret;
	struct sockaddr_in bind_addr;
	struct sockaddr_in client_addr;
	socklen_t client_addr_len = sizeof(client_addr);
	char addr_str[32];

	serv_sock = zsock_socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
	if (serv_sock < 0) {
		printk("Failed to create socket: %d\n", serv_sock);
		return serv_sock;
	}

	memset(&bind_addr, 0, sizeof(bind_addr));
	bind_addr.sin_family = AF_INET;
	bind_addr.sin_port = htons(SERVER_PORT);
	bind_addr.sin_addr.s_addr = htonl(INADDR_ANY);

	ret = zsock_bind(serv_sock, (struct sockaddr *)&bind_addr,
			 sizeof(bind_addr));
	if (ret < 0) {
		printk("Failed to bind socket: %d\n", ret);
		zsock_close(serv_sock);
		return ret;
	}

	ret = zsock_listen(serv_sock, 1);
	if (ret < 0) {
		printk("Failed to listen: %d\n", ret);
		zsock_close(serv_sock);
		return ret;
	}

	printk("TCP server listening on port %d\n", SERVER_PORT);

	client_sock = zsock_accept(serv_sock,
				   (struct sockaddr *)&client_addr,
				   &client_addr_len);
	if (client_sock < 0) {
		printk("Failed to accept: %d\n", client_sock);
		zsock_close(serv_sock);
		return client_sock;
	}

	snprintf(addr_str, sizeof(addr_str), "%d.%d.%d.%d",
		 (client_addr.sin_addr.s_addr >> 0) & 0xff,
		 (client_addr.sin_addr.s_addr >> 8) & 0xff,
		 (client_addr.sin_addr.s_addr >> 16) & 0xff,
		 (client_addr.sin_addr.s_addr >> 24) & 0xff);
	printk("Client connected from %s\n", addr_str);

	while (1) {
		/* Bound receive size to leave room for null terminator */
		ret = zsock_recv(client_sock, recv_buf,
				 sizeof(recv_buf) - 1, 0);
		if (ret < 0) {
			printk("Receive error: %d\n", ret);
			break;
		}
		if (ret == 0) {
			printk("Connection closed by client\n");
			break;
		}

		/* Safe: received bytes guaranteed < sizeof(recv_buf) */
		recv_buf[ret] = '\0';
		printk("Received %d bytes: %s\n", ret, recv_buf);
	}

	zsock_close(client_sock);
	zsock_close(serv_sock);
	return 0;
}
