Write a Zephyr RTOS application that copies a 64-byte buffer to another location in memory using DMA.

Requirements:
1. Obtain the DMA controller from the devicetree (node label: dma0)
2. Check that the device is ready before use
3. Initialize a 64-byte source buffer with a known data pattern and a 64-byte destination buffer filled with zeros
4. Configure a DMA channel to perform a memory-to-memory transfer of the entire source buffer to the destination
5. Use a callback to signal when the transfer is complete
6. Wait for completion with a reasonable timeout
7. After the transfer, verify that the destination buffer matches the source
8. Print whether the transfer succeeded or failed
9. Handle errors at each step with appropriate messages

Output ONLY the complete C source file.
