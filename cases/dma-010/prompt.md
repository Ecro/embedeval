Write a Zephyr RTOS application implementing ping-pong (double buffer) DMA for zero-copy streaming.

Requirements:
1. Obtain the DMA controller from the devicetree (node label: dma0)
2. Check that the device is ready before use
3. Define two separate 64-byte DMA buffers (buf_a and buf_b) as the ping-pong pair
4. Track which buffer is currently being filled by DMA, using a thread-safe mechanism since the index is accessed from both interrupt context and the main thread
5. When DMA completes filling one buffer, the callback must swap to the other buffer and reload DMA to continue streaming
6. Signal the main thread so it can process the just-completed buffer
7. In the main loop (at least 3 iterations), read directly from the completed DMA buffer without copying it elsewhere — this is the zero-copy requirement
8. Both buf_a and buf_b must be separate declared arrays (not a 2D array)

Output ONLY the complete C source file.
