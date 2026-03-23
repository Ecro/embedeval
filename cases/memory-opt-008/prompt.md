Write a Zephyr Kconfig configuration to minimize memory footprint for a constrained embedded target.

Produce a set of CONFIG_X=y or CONFIG_X=n lines that:

1. Disable floating-point unit support (saves ~2-4KB):
   CONFIG_FPU=n

2. Disable dynamic thread creation (saves heap overhead):
   CONFIG_DYNAMIC_THREAD=n

3. Enable minimal libc implementation (saves ~20KB over newlib):
   CONFIG_MINIMAL_LIBC=y

4. Enable nano printf backend (reduces code size over full printf):
   CONFIG_CBPRINTF_NANO=y

5. Disable newlib libc (conflicts with minimal):
   CONFIG_NEWLIB_LIBC=n

6. Disable C++ support if not needed (saves ~10KB):
   CONFIG_CPP=n

7. Set the main thread stack size to a small value:
   CONFIG_MAIN_STACK_SIZE=512

8. Enable link-time optimization if supported:
   CONFIG_LTO=y

IMPORTANT: Do NOT set CONFIG_FPU=y alongside CONFIG_MINIMAL_LIBC=y (conflicting).
All options must reduce memory usage — do not add CONFIG_DEBUG=y or similar size-increasing options.

Output ONLY the CONFIG lines, one per line.
