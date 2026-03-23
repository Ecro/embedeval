Write a Zephyr RTOS application that sends and receives data over UDP.

Requirements:
1. Include zephyr/net/socket.h and zephyr/kernel.h
2. Define server address as "192.168.1.100" and port 4242
3. In main():
   - Create a UDP socket with zsock_socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
   - Check socket return value (< 0 means error)
   - Set up a struct sockaddr_in with the server address and port (use htons for port)
   - Send the string "hello" to the server using zsock_sendto()
   - Check zsock_sendto return value for errors
   - Receive a response into a buffer using zsock_recvfrom()
   - Check zsock_recvfrom return value for errors
   - Print the number of bytes received with printk()
   - Close the socket with zsock_close()
4. Handle errors at each step with printk() and return non-zero on failure

Output ONLY the complete C source file.
