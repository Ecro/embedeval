Write a Zephyr RTOS application that performs a memory-to-memory DMA transfer with correct data integrity on a platform that has data caches.

Requirements:
1. Obtain the DMA controller from the devicetree (node label: dma0)
2. Check that the device is ready before use
3. Define a 64-byte source buffer initialized with a pattern (index % 256) and a 64-byte destination buffer initialized to zero
4. Ensure the DMA engine and the CPU see consistent data throughout the transfer — the CPU's cached view of memory and the DMA engine's view of physical memory may differ
5. Configure a DMA channel for memory-to-memory transfer of 64 bytes
6. Use a callback to signal transfer completion
7. Wait for completion with a 1-second timeout
8. After DMA completes, ensure the CPU reads the actual transferred data, not stale cached values
9. Verify buffers match; print "Cache-coherent DMA OK" or "DMA verify FAILED"

Output ONLY the complete C source file.
