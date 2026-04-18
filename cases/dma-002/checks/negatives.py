"""Negative tests for DMA Peripheral-to-Memory Transfer.

Reference: cases/dma-002/reference/main.c
Checks:    cases/dma-002/checks/static.py, behavior.py

Authored: 2026-04-19 via /negatives command
"""


NEGATIVES = [
    {
        "name": "wrong_direction",
        "description": (
            "LLM forgets peripheral-to-memory direction and uses memory-to-memory "
            "instead; ADC peripheral register won't be the DMA source."
        ),
        "mutation": lambda code: code.replace(
            "PERIPHERAL_TO_MEMORY", "MEMORY_TO_MEMORY"
        ),
        "must_fail": ["peripheral_to_memory_direction", "correct_dma_direction"],
        "factor_id": "F3.1",
    },
    {
        "name": "source_addr_incremented_wrongly",
        "description": (
            "Source address adjustment set to INCREMENT instead of NO_CHANGE. "
            "DMA would walk past the fixed MMIO peripheral register."
        ),
        "mutation": lambda code: code.replace(
            "DMA_ADDR_ADJ_NO_CHANGE", "DMA_ADDR_ADJ_INCREMENT"
        ),
        "must_fail": ["source_addr_fixed"],
        "factor_id": "F3.2",
    },
    {
        "name": "dest_addr_not_incremented",
        "description": (
            "Destination address set to NO_CHANGE, so every sample overwrites "
            "dst_buf[0]; the buffer never walks."
        ),
        "mutation": lambda code: code.replace(
            "DMA_ADDR_ADJ_INCREMENT", "DMA_ADDR_ADJ_NO_CHANGE"
        ),
        "must_fail": ["dest_addr_increments"],
        "factor_id": "F3.2",
    },
    {
        "name": "wrong_call_order",
        "description": (
            "dma_start() invoked before dma_config() — classic API-ordering bug "
            "where the channel is enabled without any configuration applied."
        ),
        "mutation": lambda code: (
            code
            .replace(
                "ret = dma_config(dma_dev, DMA_CHANNEL, &dma_cfg);",
                "__MARK_A__",
            )
            .replace(
                "ret = dma_start(dma_dev, DMA_CHANNEL);",
                "ret = dma_config(dma_dev, DMA_CHANNEL, &dma_cfg);",
                1,
            )
            .replace(
                "__MARK_A__",
                "ret = dma_start(dma_dev, DMA_CHANNEL);",
                1,
            )
        ),
        "must_fail": ["config_before_start"],
        "factor_id": "F4.1",
    },
    {
        "name": "no_completion_sync",
        "description": (
            "All DMA completion synchronization (semaphore + callback) removed; "
            "main returns before transfer completes (fire-and-forget DMA)."
        ),
        "mutation": lambda code: (
            code
            .replace(
                "k_sem_take(&dma_sem, K_SECONDS(2))",
                "k_busy_wait(2000000)",
            )
            .replace("k_sem_give(&dma_sem)", "/* removed */")
            .replace("dma_callback", "dma_done_cb")
        ),
        "must_fail": ["completion_synchronization"],
        "factor_id": "F4.2",
    },
]
