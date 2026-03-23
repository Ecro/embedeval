Write a Zephyr RTOS application that performs a DMA transfer with correct cache coherency management.

Requirements:
1. Get the DMA controller device using DEVICE_DT_GET(DT_NODELABEL(dma0))
2. Check device readiness with device_is_ready()
3. Define a source buffer of 64 bytes initialized with pattern values (index % 256)
4. Define a destination buffer of 64 bytes initialized to zero; declare it as a cache-line aligned static array using __aligned(32)
5. Before starting DMA:
   a. Call sys_cache_data_flush_range(src_buf, sizeof(src_buf)) to ensure source data is written from cache to memory
   b. Call sys_cache_data_invd_range(dst_buf, sizeof(dst_buf)) to invalidate stale destination cache lines
6. Configure a DMA channel (channel 0) for memory-to-memory transfer:
   - Set channel_direction to MEMORY_TO_MEMORY
   - Set source_data_size and dest_data_size to 1
   - Set source_burst_length and dest_burst_length to 1
   - Configure dma_block_config with source_address, dest_address, block_size = 64
7. Provide a completion callback that signals a semaphore
8. Call dma_config() then dma_start(); wait with k_sem_take() timeout 1 second
9. After DMA completes, call sys_cache_data_invd_range(dst_buf, sizeof(dst_buf)) to invalidate destination cache before CPU reads
10. Verify buffers match with memcmp; print "Cache-coherent DMA OK" or "DMA verify FAILED"

Use the Zephyr DMA API and cache API: sys_cache_data_flush_range, sys_cache_data_invd_range.

Include proper headers: zephyr/kernel.h, zephyr/device.h, zephyr/drivers/dma.h, zephyr/cache.h, string.h.

Output ONLY the complete C source file.
