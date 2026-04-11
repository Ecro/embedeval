Write a Zephyr application that uses the DMA API to transfer a buffer that the CPU has just filled.

Requirements:
1. Allocate a static aligned 256-byte source buffer and a 256-byte destination buffer.
2. Fill the source buffer from the CPU: each byte = index & 0xFF.
3. Configure a memory-to-memory DMA transfer (channel 0) using `struct dma_config` + `struct dma_block_config`; direction = `MEMORY_TO_MEMORY`.
4. Before starting the DMA, ensure the DMA engine will read the data the CPU just wrote — not stale values from a previous state of the memory system.
5. Start the transfer with `dma_start()`, wait for completion, then print `dma done`.

Output ONLY the complete C source file.
