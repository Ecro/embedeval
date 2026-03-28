Write a Zephyr RTOS application that configures two DMA channels with different priorities and runs them concurrently.

Requirements:
1. Obtain the DMA controller from the devicetree (node label: dma0)
2. Check that the device is ready before use
3. Set up two DMA channels: one high-priority and one low-priority
4. Both channels perform memory-to-memory transfers of 32 bytes each into separate destination buffers
5. Configure and validate both channels before starting either transfer
6. Start both transfers and wait for both to complete using separate completion signals
7. Print which channel completed and verify both destination buffers contain the correct data

Output ONLY the complete C source file.
