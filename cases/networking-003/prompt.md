Write a Zephyr RTOS TCP client that connects to a server with retry logic.

Requirements:
1. Include zephyr/net/socket.h, zephyr/kernel.h, and errno.h
2. Define server address as "192.168.1.100" and port 8080
3. Define MAX_RETRIES as 3
4. Implement a connect_with_retry() function that:
   - Creates a TCP socket with zsock_socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)
   - Attempts zsock_connect() in a loop, up to MAX_RETRIES times
   - On failure (return -1), checks errno for ECONNREFUSED
   - Uses exponential backoff: delay starts at 1 second, doubles each retry (1s, 2s, 4s)
   - Uses k_sleep(K_SECONDS(delay)) between retries
   - Prints the attempt number on each retry with printk()
   - Returns the socket fd on success, or -1 after all retries exhausted
5. In main():
   - Call connect_with_retry() and check result
   - On success, send "GET / HTTP/1.0\r\n\r\n" using zsock_send()
   - Close the socket with zsock_close()
   - Print "Connected" on success or "Failed to connect" on failure
6. Handle errors at each step

Output ONLY the complete C source file.
