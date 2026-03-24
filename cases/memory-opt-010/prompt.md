Write a Zephyr C program that places DMA buffers in a specific linker section for optimal placement.

Requirements:
1. Include zephyr/kernel.h and zephyr/sys/util.h
2. Define a DMA buffer placed in a named linker section (e.g., ".dma_buf") for controlled memory placement
3. Define a second buffer placed in the noinit section (uninitialized fast RAM)
4. Optionally ensure cache-line alignment on the DMA buffer
5. In main():
   - Print the address of each buffer using printk
   - Demonstrate using the DMA buffer (e.g., memset, basic write)
   - Comment explaining why the section placement is needed

CRITICAL: Do NOT use:
- __attribute__((at(0x20000000))) — this is Keil/MDK-ARM specific, NOT GCC/Zephyr
- fixed-address pointer casts — this is not portable
Use the GCC/Clang standard section attribute.

Output ONLY the complete C source file.
