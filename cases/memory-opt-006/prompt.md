Write a Zephyr RTOS configuration and C function that enables stack overflow detection and checks remaining stack space at runtime.

Part 1 - Kconfig options (output as CONFIG_X=y lines):
- Enable the necessary options for querying stack space, runtime overflow detection, and stack usage tracking

Part 2 - C code:
- Include zephyr/kernel.h
- Define a function that checks remaining stack headroom for the calling thread
- If remaining space is below a given warning threshold, print a warning message
- In main(), call the function with a threshold of 512 bytes

Output format: First output the Kconfig lines, then a blank line, then the C code.
