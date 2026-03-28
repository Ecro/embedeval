"""Static analysis checks for DMA transfer abort and error recovery."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate DMA abort/recovery code structure and required elements."""
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

    # Check 2: No FreeRTOS contamination
    has_freertos = bool(
        re.search(r"FreeRTOS\.h|xTask|vTask|xSemaphore", generated_code)
    )
    details.append(
        CheckDetail(
            check_name="no_freertos_contamination",
            passed=not has_freertos,
            expected="No FreeRTOS APIs in Zephyr application",
            actual="clean" if not has_freertos else "FreeRTOS APIs found",
            check_type="constraint",
        )
    )

    # Check 3: No Arduino contamination
    has_arduino = bool(
        re.search(r"Arduino\.h|pinMode|digitalWrite|Serial\.", generated_code)
    )
    details.append(
        CheckDetail(
            check_name="no_arduino_contamination",
            passed=not has_arduino,
            expected="No Arduino APIs in Zephyr application",
            actual="clean" if not has_arduino else "Arduino APIs found",
            check_type="constraint",
        )
    )

    # Check 4: Has timeout/abort related variable or define
    has_timeout_def = bool(
        re.search(
            r"TIMEOUT|timeout|ABORT|abort|K_MSEC|K_SECONDS",
            generated_code,
        )
    )
    details.append(
        CheckDetail(
            check_name="timeout_abort_variable_present",
            passed=has_timeout_def,
            expected="Timeout or abort related variable/define present",
            actual="present" if has_timeout_def else "missing",
            check_type="constraint",
        )
    )

    # Check 5: kernel.h included
    has_kernel_h = "zephyr/kernel.h" in generated_code
    details.append(
        CheckDetail(
            check_name="kernel_header_included",
            passed=has_kernel_h,
            expected="zephyr/kernel.h included",
            actual="present" if has_kernel_h else "missing",
            check_type="exact_match",
        )
    )

    return details
