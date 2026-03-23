"""Static analysis checks for DMA linked list multi-block with stop condition."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate DMA linked list code structure and required elements."""
    details: list[CheckDetail] = []

    # Check 1: DMA header included
    has_dma_h = "zephyr/drivers/dma.h" in generated_code
    details.append(
        CheckDetail(
            check_name="dma_header_included",
            passed=has_dma_h,
            expected="zephyr/drivers/dma.h included",
            actual="present" if has_dma_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: next_block field used
    has_next_block = "next_block" in generated_code
    details.append(
        CheckDetail(
            check_name="next_block_field_used",
            passed=has_next_block,
            expected="next_block field used to chain DMA blocks",
            actual="present" if has_next_block else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: NULL used for last block stop condition
    # Match .next_block = NULL or next_block = NULL regardless of whitespace
    has_null_stop = bool(re.search(r"next_block\s*=\s*NULL", generated_code))
    details.append(
        CheckDetail(
            check_name="last_block_next_is_null",
            passed=has_null_stop,
            expected="Last block next_block = NULL for stop condition",
            actual="present" if has_null_stop else "missing — DMA may loop or fail to stop",
            check_type="exact_match",
        )
    )

    # Check 4: block_count = 3 (with flexible whitespace)
    has_block_count_3 = bool(re.search(r"block_count\s*=\s*3", generated_code))
    details.append(
        CheckDetail(
            check_name="block_count_equals_3",
            passed=has_block_count_3,
            expected="block_count = 3 to match 3 chained blocks",
            actual="present" if has_block_count_3 else "missing or wrong block count",
            check_type="constraint",
        )
    )

    # Check 5: dma_config and dma_start present
    has_dma_api = "dma_config" in generated_code and "dma_start" in generated_code
    details.append(
        CheckDetail(
            check_name="dma_config_and_start_present",
            passed=has_dma_api,
            expected="dma_config() and dma_start() called",
            actual="present" if has_dma_api else "missing one or both DMA calls",
            check_type="exact_match",
        )
    )

    return details
