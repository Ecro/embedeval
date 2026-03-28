Write a Zephyr C program that places DMA buffers in specific linker sections for controlled memory placement.

Requirements:
1. Include zephyr/kernel.h and zephyr/sys/util.h
2. Define a DMA buffer placed in a custom-named linker section for controlled memory placement
3. Define a second buffer placed in an uninitialized section (fast RAM / noinit)
4. Ensure the DMA buffer has appropriate alignment for hardware access
5. In main():
   - Print the address of each buffer
   - Demonstrate using the DMA buffer (e.g., memset, basic write)
   - Add a comment explaining why the section placement is needed
6. Use only portable GCC/Clang attributes for section placement

Output ONLY the complete C source file.
