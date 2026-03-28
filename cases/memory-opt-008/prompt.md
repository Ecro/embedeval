Write a Zephyr Kconfig configuration to minimize the overall code and data footprint for a constrained embedded target.

Produce a set of Kconfig lines that:

1. Disable hardware features not needed by a simple application (e.g., floating-point, C++ support)
2. Select the smallest available C library and printf implementation
3. Prevent conflicting library options from being enabled simultaneously
4. Disable dynamic thread creation to save heap overhead
5. Reduce default thread stack sizes
6. Enable build-time optimization for code size

Every option should reduce memory usage. Do not include any options that increase footprint (e.g., debug features).

Output ONLY the CONFIG lines, one per line.
