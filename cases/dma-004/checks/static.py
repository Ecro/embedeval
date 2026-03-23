"""Static analysis checks for DMA scatter-gather multi-block transfer."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate DMA scatter-gather code structure and required elements."""
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

    # Check 2: next_block pointer used
    has_next_block = "next_block" in generated_code
    details.append(
        CheckDetail(
            check_name="next_block_pointer_used",
            passed=has_next_block,
            expected="next_block pointer used to chain block descriptors",
            actual="present" if has_next_block else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: block_count set in dma_config
    has_block_count = "block_count" in generated_code
    details.append(
        CheckDetail(
            check_name="block_count_set",
            passed=has_block_count,
            expected="block_count field set in struct dma_config",
            actual="present" if has_block_count else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: head_block set
    has_head_block = "head_block" in generated_code
    details.append(
        CheckDetail(
            check_name="head_block_set",
            passed=has_head_block,
            expected="head_block pointer set in struct dma_config",
            actual="present" if has_head_block else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Multiple block descriptors defined (at least 2)
    block_count = generated_code.count("dma_block_config")
    has_multiple = block_count >= 2
    details.append(
        CheckDetail(
            check_name="multiple_block_descriptors",
            passed=has_multiple,
            expected="At least 2 dma_block_config descriptors defined",
            actual=f"{block_count} dma_block_config occurrence(s)",
            check_type="exact_match",
        )
    )

    return details
