Write a Zephyr Kconfig fragment that enables deferred logging with a UART backend. The fragment should:
1. Enable CONFIG_LOG=y (logging subsystem)
2. Enable CONFIG_LOG_BACKEND_UART=y (UART output backend)
3. Enable CONFIG_LOG_MODE_DEFERRED=y (deferred mode for low-latency logging)
4. Set CONFIG_LOG_BUFFER_SIZE=2048 (buffer for deferred messages)
5. NOT enable CONFIG_LOG_MODE_IMMEDIATE=y (conflicts with deferred mode)

Output ONLY the Kconfig fragment as a plain text .conf file content.
