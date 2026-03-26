"""Negative tests for DMA error handling with callback status check.

Mutation strategy
-----------------
* missing_volatile     : strips 'volatile' → error_flag_is_volatile fails
* missing_dma_stop     : removes dma_stop lines → dma_stop_on_error fails
* error_check_before_sync: moves error flag check BEFORE k_sem_take → race condition
"""
import re


def _remove_lines(code: str, pattern: str) -> str:
    return "\n".join(line for line in code.splitlines() if pattern not in line)


def _move_error_check_before_sem(code: str) -> str:
    """Move the error flag check to before k_sem_take — introduces race condition."""
    # Remove the existing post-sem error check block
    modified = re.sub(
        r'\n\tif \(dma_error_flag[^}]+\}',
        '',
        code,
        count=1,
    )
    # Insert an early check before k_sem_take
    modified = modified.replace(
        "k_sem_take(",
        "if (dma_error_flag != 0) { return dma_error_flag; }\n\tk_sem_take(",
        1,
    )
    return modified


NEGATIVES = [
    {
        "name": "missing_volatile",
        "description": "Error flag without volatile — compiler may optimise away",
        "mutation": lambda code: code.replace("volatile int", "int").replace("volatile ", ""),
        "must_fail": ["error_flag_is_volatile"],
    },
    {
        "name": "missing_dma_stop",
        "description": "No dma_stop() on error — DMA continues corrupting memory",
        "mutation": lambda code: _remove_lines(code, "dma_stop"),
        "must_fail": ["dma_stop_on_error"],
    },
    {
        "name": "error_check_before_sync",
        "description": "Error flag checked BEFORE k_sem_take — race condition",
        "mutation": _move_error_check_before_sem,
        "must_fail": ["error_flag_read_after_sync"],
    },
    # --- Subtle mutations (should_fail — may not be caught) ---
    {
        "name": "volatile_on_wrong_variable",
        "mutation": lambda code: code.replace(
            "volatile int dma_error_flag",
            "int dma_error_flag"
        ) + "\nvolatile int _unused_volatile_marker = 0;\n",
        "should_fail": ["error_flag_is_volatile"],
        "bug_description": "volatile exists in code but on wrong variable — flag is not volatile",
    },
    {
        "name": "error_detected_but_no_return",
        "mutation": lambda code: code.replace(
            "return dma_error_flag;",
            'printk("error detected but continuing anyway\\n");'
        ),
        "should_fail": ["error_flag_causes_return"],
        "bug_description": "Error flag checked but program continues — no early return on error",
    },
]
