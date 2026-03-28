Write a Zephyr RTOS Kconfig fragment (.conf) that configures the logging subsystem with a UART backend and a filesystem backend, using deferred mode.

Requirements:
1. Enable the logging subsystem
2. Enable both UART and filesystem logging backends
3. Use deferred logging mode for minimal interrupt-context overhead
4. Set the log buffer size to 1024 bytes
5. Do NOT enable immediate logging mode (it conflicts with deferred mode)

Output ONLY the Kconfig fragment as a plain text .conf file content.
