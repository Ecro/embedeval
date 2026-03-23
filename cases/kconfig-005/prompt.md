Write a Zephyr Kconfig fragment that enables TLS networking with MbedTLS. The fragment should:
1. Enable CONFIG_NETWORKING=y (base networking stack)
2. Enable CONFIG_NET_SOCKETS=y (depends on NETWORKING)
3. Enable CONFIG_NET_SOCKETS_SOCKOPT_TLS=y (TLS socket option support, depends on NET_SOCKETS)
4. Enable CONFIG_TLS_CREDENTIALS=y (TLS credential management)
5. Enable CONFIG_MBEDTLS=y (MbedTLS library)
6. Enable CONFIG_MBEDTLS_BUILTIN=y (built-in MbedTLS, depends on MBEDTLS)
7. NOT enable conflicting TLS backends alongside MBEDTLS_BUILTIN

Output ONLY the Kconfig fragment as a plain text .conf file content.
