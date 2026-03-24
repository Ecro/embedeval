Write a Zephyr RTOS application that configures DMA in circular mode for continuous data collection.

Requirements:
1. Get the DMA controller device using DEVICE_DT_GET(DT_NODELABEL(dma0))
2. Verify the device is initialized and ready before use
3. Define two ping-pong buffers of 32 bytes each (buf_a and buf_b), initialized to zero
4. Use a global variable to track which buffer is active (current buffer index 0 or 1)
5. Configure a DMA channel (channel 0) for memory-to-memory circular transfer:
   - Set channel_direction to MEMORY_TO_MEMORY
   - Set source_data_size and dest_data_size to 1
   - Set source_burst_length and dest_burst_length to 1
   - Set cyclic to 1 in the dma_block_config to enable circular mode
   - Configure block_size = 32
6. Provide a DMA completion callback that:
   - Increments a transfer counter
   - Calls dma_reload() with the next buffer address to set up the next transfer
   - Signals a semaphore after each completed transfer
7. Call dma_config() and dma_start() to begin
8. In main, use k_sem_take() to wait for each transfer; process 4 total transfers
9. After 4 transfers call dma_stop() and print the total transfer count

Use the Zephyr DMA API: dma_config, dma_start, dma_stop, dma_reload.

Include proper headers: zephyr/kernel.h, zephyr/device.h, zephyr/drivers/dma.h.

Output ONLY the complete C source file.
