"""Negative tests for DMA memory-to-memory transfer.

Reference: cases/dma-001/reference/main.c
Checks:    cases/dma-001/checks/behavior.py

The reference:
  - dma_config(dma_dev, DMA_CHANNEL, &dma_cfg) then dma_start(dma_dev, DMA_CHANNEL).
    config_before_start: config_pos < start_pos → passes.
  - struct dma_config has .channel_direction = MEMORY_TO_MEMORY.
    memory_to_memory_direction: 'MEMORY_TO_MEMORY' present → passes.

Mutation strategy
-----------------
* start_before_config : swaps the dma_config and dma_start call blocks so
  dma_start appears first in the source. After the swap start_pos < config_pos
  → config_before_start fails.

* wrong_direction : replaces MEMORY_TO_MEMORY with PERIPHERAL_TO_MEMORY.
  The check does a literal string search for 'MEMORY_TO_MEMORY' → fails when absent.
"""


def _remove_lines(code: str, pattern: str) -> str:
    """Remove all lines containing *pattern*."""
    return "\n".join(line for line in code.splitlines() if pattern not in line)


NEGATIVES = [
    {
        "name": "start_before_config",
        "description": (
            "dma_start called before dma_config — DMA channel launched with "
            "uninitialised configuration, causing undefined transfer behaviour"
        ),
        # The check compares: config_pos = code.find('dma_config('), start_pos = code.find('dma_start(').
        # Inserting a dma_start call on a new line immediately before dma_config makes
        # dma_start appear first → start_pos < config_pos → config_before_start fails.
        "mutation": lambda code: code.replace(
            "\tret = dma_config(dma_dev, DMA_CHANNEL, &dma_cfg);",
            "\tret = dma_start(dma_dev, DMA_CHANNEL); /* BUG: start before config */\n"
            "\tret = dma_config(dma_dev, DMA_CHANNEL, &dma_cfg);",
            1,
        ),
        "must_fail": ["config_before_start"],
    },
    {
        "name": "wrong_direction",
        "description": (
            "channel_direction changed from MEMORY_TO_MEMORY to PERIPHERAL_TO_MEMORY — "
            "wrong DMA direction for a pure memory copy operation"
        ),
        # Reference: .channel_direction = MEMORY_TO_MEMORY,
        # The check does 'MEMORY_TO_MEMORY' in generated_code → fails when replaced.
        "mutation": lambda code: code.replace(
            ".channel_direction = MEMORY_TO_MEMORY,",
            ".channel_direction = PERIPHERAL_TO_MEMORY,",
        ),
        "must_fail": ["memory_to_memory_direction"],
    },
    # --- Subtle ---
    {
        "name": "missing_completion_sync",
        "mutation": lambda code: _remove_lines(code, "k_sem_take"),
        "should_fail": ["completion_synchronization"],
        "bug_description": "k_sem_take removed — main thread does not wait for DMA completion before verifying the buffer",
    },
]
