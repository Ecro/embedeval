Write a Zephyr RTOS TCP server that accepts connections and receives data safely.

Requirements:
1. Include zephyr/net/socket.h and zephyr/kernel.h
2. Define a receive buffer: `static uint8_t recv_buf[256]`
3. Create a TCP socket with zsock_socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)
4. Bind to port 4242 on INADDR_ANY
5. Call zsock_listen with backlog 1
6. Accept a single client connection with zsock_accept
7. Receive data using zsock_recv with size bounded to sizeof(recv_buf) - 1
8. Check the return value of zsock_recv (< 0 = error, 0 = connection closed)
9. Null-terminate the received data: recv_buf[received_bytes] = '\0'
10. Print the received data with printk
11. Use snprintf (not sprintf) for any string formatting
12. Close both client socket and server socket when done
13. Handle errors at each step with printk and return

Output ONLY the complete C source file.
