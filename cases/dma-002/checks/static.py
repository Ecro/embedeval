"""Static analysis checks for DMA peripheral-to-memory transfer."""

from embedeval.check_utils import has_any_api_call
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate DMA peripheral-to-memory code structure and required elements."""
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

    # Check 2: PERIPHERAL_TO_MEMORY direction set
    has_p2m = "PERIPHERAL_TO_MEMORY" in generated_code
    details.append(
        CheckDetail(
            check_name="peripheral_to_memory_direction",
            passed=has_p2m,
            expected="channel_direction = PERIPHERAL_TO_MEMORY",
            actual="present" if has_p2m else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: dma_config struct used
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

    # Check 4: dma_config() or dma_configure() API called
    # Both are valid Zephyr API spellings; accept either.
    # 2026-04-18: dma_configure variant added after Context Quality Mode
    # surfaced false negative on expert-pack runs that picked the newer form.
    has_dma_config_call = has_any_api_call(
        generated_code, ["dma_config", "dma_configure"]
    )
    details.append(
        CheckDetail(
            check_name="dma_config_called",
            passed=has_dma_config_call,
            expected="dma_config() or dma_configure() called",
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
