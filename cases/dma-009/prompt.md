Write a Zephyr RTOS application that performs a DMA memory-to-memory transfer with timeout-based abort capability.

Requirements:
1. Configure and start a DMA transfer of 256 bytes
2. Monitor the transfer with a timeout (e.g., 500ms)
3. If the transfer does not complete within the timeout, abort it cleanly
4. After abort, ensure the DMA channel is in a safe state for reuse
5. Attempt the transfer again after a successful abort
6. Track transfer statistics: completions, timeouts, and abort counts
7. Print the final statistics

The abort and recovery path must be robust — the channel must be fully stopped and reconfigured before retry.
