Write a Zephyr RTOS application that performs a scatter-gather DMA transfer, collecting data from multiple source buffers into a single contiguous destination buffer.

Requirements:
1. Obtain the DMA controller from the devicetree (node label: dma0)
2. Check that the device is ready before use
3. Define 3 source buffers of 16 bytes each, each filled with a distinct byte pattern (0xAA, 0xBB, 0xCC)
4. Define a single 48-byte destination buffer initialized to zero
5. Set up the DMA to transfer all three source buffers sequentially into the destination in one operation, without CPU intervention between segments
6. Use a callback to signal when the entire multi-segment transfer is complete
7. Wait for completion with a reasonable timeout
8. Verify the destination contains all three patterns in order
9. Print "Scatter-gather OK" or "Scatter-gather FAILED"

Output ONLY the complete C source file.
