Write a Zephyr RTOS application that performs a memory-to-memory DMA transfer.

Requirements:
1. Get the DMA controller device using DEVICE_DT_GET(DT_NODELABEL(dma0))
2. Check device readiness with device_is_ready()
3. Define a source buffer (64 bytes) initialized with a known pattern
4. Define a destination buffer (64 bytes) initialized to zero
5. Configure a DMA channel (channel 0) for memory-to-memory transfer:
   - Set channel_direction to MEMORY_TO_MEMORY
   - Set source_data_size and dest_data_size to 1 (byte transfer)
   - Set source_burst_length and dest_burst_length to 1
   - Configure a dma_block_config with source_address, dest_address, and block_size
6. Provide a DMA completion callback that signals a semaphore
7. Call dma_config() to configure the channel
8. Call dma_start() to begin the transfer
9. Wait for completion using k_sem_take() with a 1-second timeout
10. Verify the transfer by comparing source and destination buffers
11. Handle errors at each step with printk messages

Use the Zephyr DMA API: dma_config, dma_start, struct dma_config, struct dma_block_config.

Include proper headers: zephyr/kernel.h, zephyr/device.h, zephyr/drivers/dma.h.

Output ONLY the complete C source file.
