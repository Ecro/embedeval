Write a Zephyr RTOS application that performs a DMA transfer using cache-line aligned buffers.

Requirements:
1. Get the DMA controller device using DEVICE_DT_GET(DT_NODELABEL(dma0))
2. Check device readiness with device_is_ready()
3. Declare source and destination buffers of 64 bytes each with proper alignment for DMA transfers
4. Initialize the source buffer with sequential values (index % 256) and the destination buffer to zero
5. Configure DMA channel 0 for memory-to-memory transfer with block_size = 64
6. Provide a callback that signals a semaphore (K_SEM_DEFINE)
7. Call dma_config() then dma_start(); wait with k_sem_take() timeout 1 second
8. Verify buffers match with memcmp; print "Aligned DMA OK" or "DMA verify FAILED"

Use the Zephyr DMA API: dma_config, dma_start.

Include proper headers: zephyr/kernel.h, zephyr/device.h, zephyr/drivers/dma.h, string.h.

Output ONLY the complete C source file.
