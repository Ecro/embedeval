Write a Zephyr RTOS application that configures DMA for a peripheral-to-memory transfer (simulating ADC data collection).

Requirements:
1. Get the DMA controller device using DEVICE_DT_GET(DT_NODELABEL(dma0))
2. Verify the device is initialized and ready before use
3. Define a simulated peripheral address as a uint32_t constant (e.g., 0x40012400)
4. Define a destination memory buffer of 32 bytes initialized to zero
5. Configure a DMA channel (channel 0) for peripheral-to-memory transfer:
   - Set channel_direction to PERIPHERAL_TO_MEMORY
   - Set source_data_size and dest_data_size to 2 (16-bit samples)
   - Set source_burst_length to 1 and dest_burst_length to 1
   - Set source_addr_adj to DMA_ADDR_ADJ_NO_CHANGE (peripheral register is fixed)
   - Set dest_addr_adj to DMA_ADDR_ADJ_INCREMENT (memory buffer increments)
   - Configure dma_block_config with source_address as peripheral address, dest_address as buffer, block_size = 32
6. Provide a DMA completion callback that signals a semaphore
7. Call dma_config() to configure the channel
8. Call dma_start() to begin the transfer
9. Wait for completion using k_sem_take() with a 2-second timeout
10. Print "Peripheral DMA transfer complete" on success, error on timeout

Use the Zephyr DMA API: dma_config, dma_start, struct dma_config, struct dma_block_config.
Use DMA address adjustment constants: DMA_ADDR_ADJ_NO_CHANGE, DMA_ADDR_ADJ_INCREMENT.

Include proper headers: zephyr/kernel.h, zephyr/device.h, zephyr/drivers/dma.h.

Output ONLY the complete C source file.
