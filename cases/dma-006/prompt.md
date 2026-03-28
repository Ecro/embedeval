Write a Zephyr RTOS application that performs a DMA transfer using properly aligned buffers.

Requirements:
1. Obtain the DMA controller from the devicetree (node label: dma0)
2. Check that the device is ready before use
3. Declare source and destination buffers of 64 bytes each, with alignment suitable for DMA hardware access
4. Initialize the source buffer with sequential values (index % 256) and the destination to zero
5. Configure a DMA channel for memory-to-memory transfer of 64 bytes
6. Use a callback to signal completion
7. Wait for completion with a 1-second timeout
8. Verify buffers match; print "Aligned DMA OK" or "DMA verify FAILED"

Output ONLY the complete C source file.
