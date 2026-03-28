Write a Zephyr RTOS Kconfig fragment (.conf) that enables TLS-secured TCP networking with certificate-based authentication.

Requirements:
1. Enable the networking stack with BSD socket support
2. Enable TLS socket options so applications can use secure sockets
3. Enable TLS credential management for loading certificates
4. Use MbedTLS as the TLS backend (built-in, not external)
5. Do NOT enable conflicting TLS backends alongside the built-in MbedTLS

Output ONLY the Kconfig fragment as a plain text .conf file content.
