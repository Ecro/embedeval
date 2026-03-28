"""Static analysis checks for DMA error handling with callback status check."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate DMA error handling code structure and required elements."""
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

    # Check 2: volatile applied specifically to the error flag variable (not just any variable).
    # Reject code that declares `volatile` elsewhere (e.g. on a DMA buffer) while the flag itself
    # is non-volatile — the LLM blind spot being targeted here.
    has_volatile_flag = bool(re.search(
        r'volatile\s+(?:int|uint\w+|bool|_Bool)\s+\w*(?:error|err|fail|fault|status)\w*',
        generated_code,
    )) or bool(re.search(
        r'(?:int|uint\w+|bool|_Bool)\s+volatile\s+\w*(?:error|err|fail|fault|status)\w*',
        generated_code,
    ))
    details.append(
        CheckDetail(
            check_name="volatile_error_flag",
            passed=has_volatile_flag,
            expected="volatile applied to the error/err flag variable itself",
            actual="present" if has_volatile_flag else "missing — volatile on wrong variable or absent",
            check_type="exact_match",
        )
    )

    # Check 3: dma_stop called
    has_dma_stop = "dma_stop" in generated_code
    details.append(
        CheckDetail(
            check_name="dma_stop_called",
            passed=has_dma_stop,
            expected="dma_stop() called to halt DMA on error",
            actual="present" if has_dma_stop else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: DMA callback present
    has_callback = "dma_callback" in generated_code or "callback" in generated_code
    details.append(
        CheckDetail(
            check_name="dma_callback_defined",
            passed=has_callback,
            expected="DMA callback function defined",
            actual="present" if has_callback else "missing",
            check_type="exact_match",
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
