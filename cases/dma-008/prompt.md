Write a Zephyr RTOS application that performs a DMA transfer with error detection in the completion callback.

Requirements:
1. Get the DMA controller device using DEVICE_DT_GET(DT_NODELABEL(dma0))
2. Verify the DMA device is initialized and available before use
3. Declare a global error flag that can be safely shared between the DMA callback and main thread
4. Implement a DMA callback with signature: void dma_callback(const struct device *dev, void *user_data, uint32_t channel, int status)
5. In the callback:
   - Check the status parameter: if status != 0, record the error status and call dma_stop(dev, channel)
   - If status == 0, signal the completion semaphore
6. Configure DMA channel 0 for a 64-byte memory-to-memory transfer
7. Call dma_config() then dma_start(); wait with k_sem_take() timeout 1 second
8. After the wait, check the error flag: if non-zero, print "DMA error: %d" and return error
10. If no error, verify data with memcmp and print "DMA OK" or "DMA verify FAILED"

Use the Zephyr DMA API: dma_config, dma_start, dma_stop.

Include proper headers: zephyr/kernel.h, zephyr/device.h, zephyr/drivers/dma.h, string.h.

Output ONLY the complete C source file.
