Write a Zephyr RTOS application that performs a DMA transfer with error detection in the completion callback.

Requirements:
1. Get the DMA controller device using DEVICE_DT_GET(DT_NODELABEL(dma0))
2. Check device readiness with device_is_ready()
3. Declare a volatile global error flag: volatile int dma_error_flag = 0
4. The error flag MUST be volatile to prevent compiler optimization
5. Implement a DMA callback with signature: void dma_callback(const struct device *dev, void *user_data, uint32_t channel, int status)
6. In the callback:
   - Check the status parameter: if status != 0, set dma_error_flag = status and call dma_stop(dev, channel)
   - If status == 0, signal the completion semaphore
7. Configure DMA channel 0 for a 64-byte memory-to-memory transfer
8. Call dma_config() then dma_start(); wait with k_sem_take() timeout 1 second
9. After the wait, check dma_error_flag: if non-zero, print "DMA error: %d" and return error
10. If no error, verify data with memcmp and print "DMA OK" or "DMA verify FAILED"

Use the Zephyr DMA API: dma_config, dma_start, dma_stop.

Include proper headers: zephyr/kernel.h, zephyr/device.h, zephyr/drivers/dma.h, string.h.

Output ONLY the complete C source file.
