Write a Zephyr RTOS application that uses DMA in circular mode for continuous data collection with ping-pong buffers.

Requirements:
1. Obtain the DMA controller from the devicetree (node label: dma0)
2. Check that the device is ready before use
3. Define two 32-byte buffers (buf_a and buf_b) for alternating DMA targets
4. Track which buffer is currently active
5. Configure DMA to automatically restart after each transfer completes (circular/continuous mode)
6. On each transfer completion, reload the DMA to fill the next buffer
7. Signal the main thread after each transfer so it can process the completed buffer
8. Process at least 4 transfers in the main loop, then stop the DMA
9. Print the total number of completed transfers

Output ONLY the complete C source file.
