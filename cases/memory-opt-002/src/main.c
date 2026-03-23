# Minimal memory footprint Kconfig fragment for Zephyr RTOS
# Suitable for Cortex-M0 class targets with <32KB RAM

# Reduce main thread stack from default 1024 to 512 bytes
CONFIG_MAIN_STACK_SIZE=512

# Reduce ISR stack from default 2048 to 512 bytes
CONFIG_ISR_STACK_SIZE=512

# Use minimal C library (smaller than newlib, no printf float support)
CONFIG_MINIMAL_LIBC=y

# Disable system heap entirely — use slabs or static buffers instead
CONFIG_HEAP_MEM_POOL_SIZE=0
