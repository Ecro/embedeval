Write a Zephyr RTOS application that uses DMA linked-list mode to chain three memory blocks in sequence.

Requirements:
1. Get the DMA controller device using DEVICE_DT_GET(DT_NODELABEL(dma0))
2. Check device readiness with device_is_ready()
3. Define three source buffers (src0, src1, src2) of 16 bytes each, initialized with distinct values
4. Define three destination buffers (dst0, dst1, dst2) of 16 bytes each, initialized to zero
5. Define three struct dma_block_config entries (block0, block1, block2):
   - block0: source_address=src0, dest_address=dst0, block_size=16, next_block=&block1
   - block1: source_address=src1, dest_address=dst1, block_size=16, next_block=&block2
   - block2: source_address=src2, dest_address=dst2, block_size=16, next_block=NULL (STOP condition)
6. The last block MUST have next_block = NULL to stop DMA (not circular/loop)
7. Set block_count = 3 in dma_config to match the actual number of blocks
8. Provide a callback that signals a semaphore on completion
9. Call dma_config() then dma_start(); wait with k_sem_take() timeout 2 seconds
10. Verify all three destination buffers with memcmp; print "Multi-block DMA OK" or "FAILED"

Use the Zephyr DMA API: dma_config, dma_start.

Include proper headers: zephyr/kernel.h, zephyr/device.h, zephyr/drivers/dma.h, string.h.

Output ONLY the complete C source file.
