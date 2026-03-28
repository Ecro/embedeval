Write a Zephyr RTOS Kconfig fragment (prj.conf) that minimizes RAM usage for a very constrained target (e.g., Cortex-M0 with less than 32KB RAM).

Requirements:
1. Reduce thread stack sizes to reasonable minimums
2. Choose the smallest available C library implementation
3. Disable the system heap entirely
4. Ensure no conflicting library options are enabled
5. Add a comment explaining each setting's purpose

Output ONLY the complete prj.conf Kconfig fragment.
