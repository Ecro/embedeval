Write a Zephyr RTOS application that performs a scatter-gather DMA transfer using linked block descriptors.

Requirements:
1. Get the DMA controller device using DEVICE_DT_GET(DT_NODELABEL(dma0))
2. Verify the device is initialized and ready before use
3. Define 3 source buffers of 16 bytes each (src0, src1, src2), initialized with different fill patterns (0xAA, 0xBB, 0xCC)
4. Define a single destination buffer of 48 bytes initialized to zero
5. Create 3 struct dma_block_config descriptors, one per source buffer:
   - block 0: source_address = src0, dest_address = dst+0,  block_size = 16
   - block 1: source_address = src1, dest_address = dst+16, block_size = 16
   - block 2: source_address = src2, dest_address = dst+32, block_size = 16
6. Link the blocks via next_block pointer: block0.next_block = &block1, block1.next_block = &block2, block2.next_block = NULL
7. Configure struct dma_config:
   - Set channel_direction to MEMORY_TO_MEMORY
   - Set block_count to 3
   - Set head_block to &block0
8. Provide a completion callback that signals a semaphore
9. Call dma_config() then dma_start(); wait for completion with k_sem_take()
10. Verify the destination buffer contains the expected pattern (0xAA * 16, 0xBB * 16, 0xCC * 16)
11. Print "Scatter-gather OK" or "Scatter-gather FAILED"

Use the Zephyr DMA API: dma_config, dma_start, struct dma_config, struct dma_block_config.

Include proper headers: zephyr/kernel.h, zephyr/device.h, zephyr/drivers/dma.h, string.h.

Output ONLY the complete C source file.
