Write a Zephyr C program that places DMA buffers in a specific linker section for optimal placement.

Requirements:
1. Include zephyr/kernel.h and zephyr/sys/util.h
2. Define a DMA buffer placed in a named section using GCC attribute:
   static uint8_t dma_buf[1024] __attribute__((section(".dma_buf")));
   OR using Zephyr macro:
   static uint8_t dma_buf[1024] Z_GENERIC_SECTION(.dma_buf);
3. Define a second buffer in the noinit section (uninitialized fast RAM):
   static uint8_t fast_buf[512] __attribute__((section(".noinit")));
4. Optionally use __aligned(32) to ensure cache line alignment:
   __attribute__((section(".dma_buf"), aligned(32)))
5. In main():
   - Print the address of each buffer using printk
   - Demonstrate using the DMA buffer (e.g., memset, basic write)
   - Comment explaining why the section placement is needed

CRITICAL: Do NOT use:
- __attribute__((at(0x20000000))) — this is Keil/MDK-ARM specific, NOT GCC/Zephyr
- volatile pointers to fixed addresses — this is not portable
Use __attribute__((section("..."))) which is the GCC/Clang standard.

Output ONLY the complete C source file.
