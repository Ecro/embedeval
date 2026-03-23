Write a Zephyr Kconfig fragment that enables USERSPACE support with the Memory Protection Unit (MPU).

Requirements:
1. Enable CONFIG_USERSPACE=y (user-space thread support)
2. Enable CONFIG_MPU=y (Memory Protection Unit, required by USERSPACE)
3. Enable CONFIG_ARM_MPU=y (ARM MPU hardware implementation)
4. Set CONFIG_MAX_DOMAIN_PARTITIONS=16 (maximum memory domain partitions)
5. Set CONFIG_HEAP_MEM_POOL_SIZE=16384 (heap pool required for user thread stacks)
6. Do NOT set CONFIG_MAX_THREAD_BYTES to a value less than 1 (must be at least 1)
7. Do NOT enable CONFIG_ARC_MPU=y alongside CONFIG_ARM_MPU=y (platform-specific, mutually exclusive)
8. Do NOT enable CONFIG_USERSPACE without CONFIG_MPU=y

Output ONLY the Kconfig fragment as a plain text .conf file content.
