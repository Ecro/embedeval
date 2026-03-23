#include <zephyr/kernel.h>
#include <zephyr/net/coap.h>
#include <zephyr/net/socket.h>
#include <string.h>

#define SERVER_ADDR  "192.168.1.100"
#define SERVER_PORT  5683
#define RESOURCE_PATH "sensors/temp"

int main(void)
{
	int sock;
	int ret;
	struct sockaddr_in server;
	socklen_t addrlen = sizeof(server);
	uint8_t req_buf[256];
	uint8_t rsp_buf[256];
	struct coap_packet request;
	struct coap_packet response;
	static uint8_t token[] = {0x01, 0x02};

	sock = zsock_socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
	if (sock < 0) {
		printk("Failed to create socket: %d\n", sock);
		return sock;
	}

	memset(&server, 0, sizeof(server));
	server.sin_family = AF_INET;
	server.sin_port = htons(SERVER_PORT);
	net_addr_pton(AF_INET, SERVER_ADDR, &server.sin_addr);

	ret = coap_packet_init(&request, req_buf, sizeof(req_buf),
			       COAP_VERSION_1, COAP_TYPE_CON,
			       sizeof(token), token,
			       COAP_METHOD_GET, coap_next_id());
	if (ret < 0) {
		printk("Failed to init CoAP packet: %d\n", ret);
		zsock_close(sock);
		return ret;
	}

	ret = coap_packet_append_option(&request, COAP_OPTION_URI_PATH,
					RESOURCE_PATH, strlen(RESOURCE_PATH));
	if (ret < 0) {
		printk("Failed to append URI-path option: %d\n", ret);
		zsock_close(sock);
		return ret;
	}

	ret = zsock_sendto(sock, request.data, request.offset, 0,
			   (struct sockaddr *)&server, sizeof(server));
	if (ret < 0) {
		printk("Failed to send CoAP request: %d\n", ret);
		zsock_close(sock);
		return ret;
	}

	printk("CoAP GET sent to %s/%s\n", SERVER_ADDR, RESOURCE_PATH);

	ret = zsock_recvfrom(sock, rsp_buf, sizeof(rsp_buf), 0,
			     (struct sockaddr *)&server, &addrlen);
	if (ret < 0) {
		printk("Failed to receive response: %d\n", ret);
		zsock_close(sock);
		return ret;
	}

	ret = coap_packet_parse(&response, rsp_buf, ret, NULL, 0);
	if (ret < 0) {
		printk("Failed to parse CoAP response: %d\n", ret);
		zsock_close(sock);
		return ret;
	}

	uint8_t code = coap_header_get_code(&response);

	printk("CoAP response code: 0x%02x\n", code);

	zsock_close(sock);
	return 0;
}
