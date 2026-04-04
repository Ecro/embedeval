"""Negative tests for DMA transfer abort and error recovery.

Reference: cases/dma-009/reference/main.c
Checks:    cases/dma-009/checks/behavior.py

The reference:
  - calls dma_stop(dma_dev, DMA_CHANNEL) on timeout to abort the transfer
  - calls dma_start(dma_dev, DMA_CHANNEL) at least twice:
      once in the retry loop and once for the final channel-reuse transfer

Mutation strategy
-----------------
* no_dma_stop : removes the dma_stop call entirely.
  The check dma_stop_called looks for "dma_stop" in stripped code — will fail.

* single_dma_start : collapses the final standalone dma_start call so only one
  dma_start token remains in the source.  The check dma_start_called_twice
  requires at least 2 occurrences — will fail.
"""


def _remove_lines(code: str, pattern: str) -> str:
    return "\n".join(line for line in code.splitlines() if pattern not in line)


NEGATIVES = [
    {
        "name": "no_dma_stop",
        "description": (
            "dma_stop() never called on timeout — in-progress DMA channel is "
            "abandoned and cannot be safely reconfigured or restarted"
        ),
        "mutation": lambda code: _remove_lines(code, "dma_stop"),
        "must_fail": ["dma_stop_called"],
    },
    {
        "name": "single_dma_start",
        "description": (
            "Only one dma_start() call present — the retry loop never re-starts "
            "the channel, so DMA recovery after timeout does not work"
        ),
        # The reference has dma_start twice: once in the loop and once in the
        # final channel-reuse block.  Replace the second occurrence with a
        # comment so the token count drops to 1.
        "mutation": lambda code: code.replace(
            "ret = dma_start(dma_dev, DMA_CHANNEL);\n\t\tif (ret == 0) {",
            "/* dma_start skipped */\n\t\tif (0 == 0) {",
        ),
        "must_fail": ["dma_start_called_twice"],
    },
]
