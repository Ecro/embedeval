"""Static analysis checks for DMA memory-to-memory transfer."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate DMA code structure and required elements."""
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

    # Check 2: dma_config struct used
    has_dma_cfg = "struct dma_config" in generated_code
    details.append(
        CheckDetail(
            check_name="dma_config_struct",
            passed=has_dma_cfg,
            expected="struct dma_config defined",
            actual="present" if has_dma_cfg else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: dma_block_config struct used
    has_block_cfg = "dma_block_config" in generated_code
    details.append(
        CheckDetail(
            check_name="dma_block_config_struct",
            passed=has_block_cfg,
            expected="struct dma_block_config defined",
            actual="present" if has_block_cfg else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: dma_config() API called
    has_dma_config_call = "dma_config(" in generated_code
    details.append(
        CheckDetail(
            check_name="dma_config_called",
            passed=has_dma_config_call,
            expected="dma_config() called",
            actual="present" if has_dma_config_call else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: dma_start() API called
    has_dma_start = "dma_start(" in generated_code
    details.append(
        CheckDetail(
            check_name="dma_start_called",
            passed=has_dma_start,
            expected="dma_start() called",
            actual="present" if has_dma_start else "missing",
            check_type="exact_match",
        )
    )

    return details
