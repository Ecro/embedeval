Write a Zephyr RTOS application that uses DMA to collect data from a peripheral's data register into a memory buffer, simulating ADC sample collection.

Requirements:
1. Obtain the DMA controller from the devicetree (node label: dma0)
2. Check that the device is ready before use
3. The peripheral has a single 16-bit data register at a fixed address (e.g., 0x40012400) that does not auto-increment
4. Transfer 32 bytes of 16-bit samples from the peripheral register into a RAM buffer
5. The destination buffer address must advance through memory as samples arrive
6. Use a callback to signal transfer completion
7. Wait for completion with a reasonable timeout
8. Print whether the transfer succeeded or failed

Output ONLY the complete C source file.
