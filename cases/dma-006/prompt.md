Write a Zephyr RTOS application that performs a DMA transfer using cache-line aligned buffers.

Requirements:
1. Get the DMA controller device using DEVICE_DT_GET(DT_NODELABEL(dma0))
2. Check device readiness with device_is_ready()
3. Define a source buffer of 64 bytes: static uint8_t src_buf[64] __aligned(32)
4. Define a destination buffer of 64 bytes: static uint8_t dst_buf[64] __aligned(32)
5. Both buffers MUST use __aligned(32) — do NOT use memalign() or posix_memalign() (not available in Zephyr RTOS)
6. Initialize src_buf with sequential values (index % 256) and dst_buf to zero
7. Configure DMA channel 0 for memory-to-memory transfer with block_size = 64
8. Provide a callback that signals a semaphore (K_SEM_DEFINE)
9. Call dma_config() then dma_start(); wait with k_sem_take() timeout 1 second
10. Verify buffers match with memcmp; print "Aligned DMA OK" or "DMA verify FAILED"

Use the Zephyr DMA API: dma_config, dma_start.

Include proper headers: zephyr/kernel.h, zephyr/device.h, zephyr/drivers/dma.h, string.h.

Output ONLY the complete C source file.
