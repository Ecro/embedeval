Write a Zephyr RTOS HTTPS client that performs a GET request using TLS.

Requirements:
1. Include zephyr/net/http/client.h, zephyr/net/tls_credentials.h, zephyr/net/socket.h, and zephyr/kernel.h
2. Define the server host as "example.com", port 443, and path "/"
3. Define a TLS security tag as SEC_TAG 1
4. Declare a static const char ca_certificate[] containing a PEM placeholder string (any non-empty string)
5. In main():
   - Register the CA certificate with tls_credential_add() using TLS_CREDENTIAL_CA_CERTIFICATE and the SEC_TAG
   - Check tls_credential_add() return value
   - Create a TLS socket: zsock_socket(AF_INET, SOCK_STREAM, IPPROTO_TLS_1_2)
   - Set TLS_SEC_TAG_LIST socket option using zsock_setsockopt() with SOL_TLS and TLS_SEC_TAG_LIST
   - Set TLS_HOSTNAME socket option using zsock_setsockopt() with the server hostname
   - Set up server address (port 443) and call zsock_connect()
   - Set up struct http_request with method HTTP_GET, host, path, and a response callback
   - Implement a response_cb() function that prints received data length
   - Call http_client_req() with a timeout of 5 seconds
   - Close socket with zsock_close()
6. Check all return values and print errors

Output ONLY the complete C source file.
