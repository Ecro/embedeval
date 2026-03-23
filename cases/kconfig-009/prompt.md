Write a Zephyr Kconfig fragment that enables the Zephyr shell with logging backend integration.

Requirements:
1. Enable CONFIG_SHELL=y (Zephyr shell subsystem)
2. Enable CONFIG_SHELL_LOG_BACKEND=y (shell as a logging backend, depends on SHELL)
3. Enable CONFIG_LOG=y (logging subsystem, required by SHELL_LOG_BACKEND)
4. Set CONFIG_LOG_BUFFER_SIZE=4096 (sufficient log buffer for shell output)
5. Do NOT enable CONFIG_LOG_MINIMAL=y (incompatible with SHELL_LOG_BACKEND — mutual exclusion)
6. Do NOT enable CONFIG_SHELL_LOG_BACKEND without CONFIG_LOG=y

Output ONLY the Kconfig fragment as a plain text .conf file content.
