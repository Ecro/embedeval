"""Static checks for dma-010: DMA cache coherence handling."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []

    has_dma_h = "drivers/dma.h" in generated_code
    details.append(
        CheckDetail(
            check_name="dma_header_included",
            passed=has_dma_h,
            expected="zephyr/drivers/dma.h included",
            actual="present" if has_dma_h else "missing",
            check_type="exact_match",
        )
    )

    has_dma_config = (
        "dma_config" in generated_code and "dma_block_config" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="dma_structs_used",
            passed=has_dma_config,
            expected="dma_config and dma_block_config structs used",
            actual="present" if has_dma_config else "missing",
            check_type="constraint",
        )
    )

    has_start = "dma_start" in generated_code
    details.append(
        CheckDetail(
            check_name="dma_start_called",
            passed=has_start,
            expected="dma_start() called",
            actual="present" if has_start else "missing",
            check_type="exact_match",
        )
    )

    has_flush = bool(
        re.search(
            r"sys_cache_data_flush_range|"
            r"sys_cache_data_flush_all|"
            r"cache_data_flush",
            generated_code,
        )
    )
    details.append(
        CheckDetail(
            check_name="cache_flush_before_dma",
            passed=has_flush,
            expected=(
                "sys_cache_data_flush_range() called before DMA start so the "
                "DMA engine reads the CPU's latest stores"
            ),
            actual="present"
            if has_flush
            else "missing — DMA may read stale cached data",
            check_type="constraint",
        )
    )

    has_aligned = bool(re.search(r"__aligned\s*\(\s*\d+\s*\)", generated_code))
    details.append(
        CheckDetail(
            check_name="buffer_alignment",
            passed=has_aligned,
            expected="Buffers declared with __aligned() for cache-line alignment",
            actual="present" if has_aligned else "missing — cache line split risk",
            check_type="constraint",
        )
    )

    has_mem_to_mem = "MEMORY_TO_MEMORY" in generated_code
    details.append(
        CheckDetail(
            check_name="direction_memory_to_memory",
            passed=has_mem_to_mem,
            expected="channel_direction = MEMORY_TO_MEMORY",
            actual="present" if has_mem_to_mem else "missing",
            check_type="exact_match",
        )
    )

    return details
