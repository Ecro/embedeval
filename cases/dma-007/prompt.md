Write a Zephyr RTOS application that configures two DMA channels with different priorities.

Requirements:
1. Get the DMA controller device using DEVICE_DT_GET(DT_NODELABEL(dma0))
2. Check device readiness with device_is_ready()
3. Define channel 0 as HIGH priority and channel 1 as LOW priority
4. Configure channel 0 with channel_priority = 0 (highest) and channel 1 with channel_priority = 1 (lower)
   (Lower numeric value = higher priority in Zephyr DMA)
5. Both channels perform memory-to-memory transfers of 32 bytes each to separate buffers
6. Both dma_config() calls must succeed before either dma_start() is called
7. Start both channels: call dma_start() for channel 0 first, then channel 1
8. Wait for both to complete using two semaphores (one per channel callback)
9. Print "High priority channel done" and "Low priority channel done" in callback order
10. Verify both destination buffers are correct with memcmp

Use the Zephyr DMA API: dma_config, dma_start.

Include proper headers: zephyr/kernel.h, zephyr/device.h, zephyr/drivers/dma.h, string.h.

Output ONLY the complete C source file.
