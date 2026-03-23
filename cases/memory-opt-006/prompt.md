Write a Zephyr RTOS configuration that enables stack overflow detection and a C function that checks remaining stack space at runtime.

Part 1 - Kconfig options (output as CONFIG_X=y lines):
- Enable CONFIG_THREAD_STACK_INFO=y to allow stack space queries
- Enable CONFIG_STACK_SENTINEL=y for runtime sentinel detection
- Enable CONFIG_STACK_USAGE=y to track stack usage statistics

Part 2 - C code:
- Include zephyr/kernel.h
- Define a function: void check_stack_headroom(size_t warn_threshold)
  - Call k_thread_stack_space_get(k_current_get(), &unused) to get remaining stack
  - If unused < warn_threshold, call LOG_WRN or printk to warn about low stack
  - Return or take action if stack is critically low
- In main(), call check_stack_headroom with a threshold (e.g., 512 bytes)

Output format: First output the Kconfig lines (CONFIG_X=y), then a blank line, then the C code.

IMPORTANT: Use k_thread_stack_space_get() — this is the correct Zephyr API for checking
remaining stack space. Do NOT use a custom stack canary pattern or __builtin_frame_address.
