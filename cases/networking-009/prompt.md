Write a Zephyr RTOS WebSocket client that connects over TLS (WSS).

Requirements:
1. Include zephyr/net/websocket.h, zephyr/net/tls_credentials.h, zephyr/net/socket.h, and zephyr/kernel.h
2. Define server host "ws.example.com", port 443, and path "/ws"
3. Define a security tag constant: #define SEC_TAG 1
4. Register a TLS CA certificate using tls_credential_add() BEFORE creating the socket
   - Use TLS_CREDENTIAL_CA_CERTIFICATE type
   - Use a placeholder certificate string (static const char ca_cert[])
5. Create a TLS socket: zsock_socket(AF_INET, SOCK_STREAM, IPPROTO_TLS_1_2)
6. Set TLS_SEC_TAG_LIST socket option with the sec_tag array
7. Set TLS_HOSTNAME socket option to the server host string
8. Connect the TCP socket with zsock_connect
9. Call websocket_connect() with a struct websocket_request including the host and url path
10. Check the return value of websocket_connect (< 0 = error)
11. Send a text frame using websocket_send_msg() with WEBSOCKET_OPCODE_DATA_TEXT
12. Receive a frame using websocket_recv_msg()
13. Close the websocket with websocket_disconnect()
14. Close the TCP socket with zsock_close()
15. Do NOT hardcode credentials as raw values in the code body — use a named constant array

Output ONLY the complete C source file.
