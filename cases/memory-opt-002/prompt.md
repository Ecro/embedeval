Write a Zephyr RTOS Kconfig fragment (prj.conf) that minimizes memory footprint via stack size reduction and libc selection.

Requirements:
1. Set CONFIG_MAIN_STACK_SIZE=512 to reduce the main thread stack
2. Set CONFIG_ISR_STACK_SIZE=512 to reduce the ISR stack
3. Enable CONFIG_MINIMAL_LIBC=y to use the minimal C library (smaller than newlib)
4. Ensure CONFIG_NEWLIB_LIBC is NOT enabled (conflicts with MINIMAL_LIBC)
5. Set CONFIG_HEAP_MEM_POOL_SIZE=0 to disable the system heap entirely
6. Add a comment explaining each setting's purpose

These settings are appropriate for very constrained targets (Cortex-M0, <32KB RAM).
The stack sizes of 512 bytes are a reasonable minimum — smaller values cause stack
overflows in typical applications.

Output ONLY the complete prj.conf Kconfig fragment.
