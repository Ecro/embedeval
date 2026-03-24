Write a Zephyr RTOS application implementing ping-pong (double buffer) DMA for zero-copy streaming.

Requirements:
1. Get the DMA controller device using DEVICE_DT_GET(DT_NODELABEL(dma0))
2. Verify the device is initialized and ready before use
3. Define two separate DMA buffers of 64 bytes each: buf_a and buf_b — these are the ping-pong buffers
4. Declare an atomic index: static atomic_t active_buf_idx = ATOMIC_INIT(0)
5. The DMA callback (called on each buffer completion) must:
   - Read the current active_buf_idx using atomic_get()
   - Swap it atomically: atomic_set(&active_buf_idx, 1 - atomic_get(&active_buf_idx))
   - Reload DMA to fill the NEXT buffer (not the one just completed): call dma_reload()
   - Signal a semaphore so the CPU can process the completed buffer
6. In the main loop (run at least 3 iterations):
   - Take the semaphore (k_sem_take with K_SECONDS(1))
   - Determine which buffer DMA just filled (the one NOT currently being filled)
   - Process that buffer (e.g. print first byte) WITHOUT memcpy to another buffer
7. Do NOT use memcpy between buffers — zero-copy means CPU reads directly from DMA buffer
8. Both buf_a and buf_b must be separate declared arrays (not a 2D array)

Use the Zephyr DMA API: dma_config, dma_start, dma_reload.

Include proper headers: zephyr/kernel.h, zephyr/device.h, zephyr/drivers/dma.h.

Output ONLY the complete C source file.
