Write a Zephyr application that issues a single DMA request transferring three NON-CONTIGUOUS 64-byte source buffers (`src_a`, `src_b`, `src_c`) to three non-contiguous destination buffers (`dst_a`, `dst_b`, `dst_c`).

Requirements:
1. Use the Zephyr DMA API (`zephyr/drivers/dma.h`).
2. The three transfers must be issued as ONE `dma_start()` call — NOT three separate calls.
3. Source and destination pairs are independent — their addresses are unrelated to each other.
4. Use `struct dma_config` + `struct dma_block_config` and wire the block descriptors so all three pairs complete from a single start.
5. After completion print `transfer complete`.

Output ONLY the complete C source file.
