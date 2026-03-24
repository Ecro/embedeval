Write a Zephyr RTOS application that performs a DMA transfer with correct cache coherency management.

Requirements:
1. Get the DMA controller device using DEVICE_DT_GET(DT_NODELABEL(dma0))
2. Check device readiness with device_is_ready()
3. Define a source buffer of 64 bytes initialized with pattern values (index % 256)
4. Define a destination buffer of 64 bytes initialized to zero; ensure it is properly aligned for DMA operations
5. Before starting DMA, handle cache coherency:
   a. Flush source data from cache to memory so the DMA controller sees current values
   b. Invalidate stale destination cache lines so the CPU does not read old cached data after DMA
6. Configure a DMA channel (channel 0) for memory-to-memory transfer:
   - Set channel_direction to MEMORY_TO_MEMORY
   - Set source_data_size and dest_data_size to 1
   - Set source_burst_length and dest_burst_length to 1
   - Configure dma_block_config with source_address, dest_address, block_size = 64
7. Provide a completion callback that signals a semaphore
8. Call dma_config() then dma_start(); wait with k_sem_take() timeout 1 second
9. After DMA completes, invalidate the destination cache before the CPU reads the transferred data
10. Verify buffers match with memcmp; print "Cache-coherent DMA OK" or "DMA verify FAILED"

Use the Zephyr DMA API and cache coherency API.

Include proper headers: zephyr/kernel.h, zephyr/device.h, zephyr/drivers/dma.h, zephyr/cache.h, string.h.

Output ONLY the complete C source file.
