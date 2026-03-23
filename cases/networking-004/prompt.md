Write a Zephyr RTOS CoAP client that sends a GET request to a resource.

Requirements:
1. Include zephyr/net/coap.h, zephyr/net/socket.h, and zephyr/kernel.h
2. Define server address as "192.168.1.100" and port 5683 (standard CoAP port)
3. Define the resource path as "sensors/temp"
4. In main():
   - Create a UDP socket with zsock_socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
   - Set up server address with htons(5683)
   - Declare a uint8_t buffer[256] for the CoAP packet
   - Initialize a CoAP packet with coap_packet_init() using COAP_TYPE_CON and COAP_METHOD_GET
   - Set a non-zero token (e.g., a static uint8_t token[] = {0x01, 0x02})
   - Add the URI-path option using coap_packet_append_option() with COAP_OPTION_URI_PATH
   - Transmit the packet with zsock_sendto()
   - Receive the response into a separate buffer with zsock_recvfrom()
   - Parse the response with coap_packet_parse()
   - Print the CoAP response code using coap_header_get_code()
   - Close the socket with zsock_close()
5. Check return values at each step and print errors with printk()

Output ONLY the complete C source file.
