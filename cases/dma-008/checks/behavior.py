"""Behavioral checks for DMA error handling with callback status check."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate DMA error handling behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: Callback inspects the status parameter (status != 0 check)
    has_status_check = (
        "status != 0" in generated_code
        or "status < 0" in generated_code
        or "if (status)" in generated_code
        or "if(status)" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="callback_checks_status_parameter",
            passed=has_status_check,
            expected="DMA callback checks status parameter for non-zero (error) value",
            actual="present" if has_status_check else "missing status check in callback",
            check_type="constraint",
        )
    )

    # Check 2: Error flag is volatile
    has_volatile_flag = "volatile" in generated_code
    details.append(
        CheckDetail(
            check_name="error_flag_is_volatile",
            passed=has_volatile_flag,
            expected="Error flag declared as volatile to prevent compiler optimization",
            actual="present" if has_volatile_flag else "missing volatile — flag may be optimized away",
            check_type="constraint",
        )
    )

    # Check 3: dma_stop called on error (in callback or after)
    dma_stop_pos = generated_code.find("dma_stop(")
    has_dma_stop = dma_stop_pos != -1
    details.append(
        CheckDetail(
            check_name="dma_stop_on_error",
            passed=has_dma_stop,
            expected="dma_stop() called when DMA error is detected",
            actual="present" if has_dma_stop else "missing — DMA channel not stopped on error",
            check_type="constraint",
        )
    )

    # Check 4: Error flag checked after semaphore wait in main
    # Use rfind to find the LAST usage of the error flag (the check in main, not the declaration)
    sem_pos = generated_code.find("k_sem_take")
    error_flag_name = (
        "dma_error_flag" if "dma_error_flag" in generated_code
        else "error_flag" if "error_flag" in generated_code
        else None
    )
    if error_flag_name:
        # Find the last occurrence (the check in main, after k_sem_take)
        error_flag_last_pos = generated_code.rfind(error_flag_name)
    else:
        error_flag_last_pos = -1
    error_checked_after_wait = (
        sem_pos != -1
        and error_flag_last_pos != -1
        and error_flag_last_pos > sem_pos
    )
    details.append(
        CheckDetail(
            check_name="error_flag_checked_after_wait",
            passed=error_checked_after_wait,
            expected="Error flag checked after semaphore wait (in main, not just in callback)",
            actual="correct order" if error_checked_after_wait else "missing or wrong order",
            check_type="constraint",
        )
    )

    # Check 5: dma_stop present in code (error path guard)
    has_stop_near_error = has_dma_stop
    details.append(
        CheckDetail(
            check_name="dma_stop_in_error_path",
            passed=has_stop_near_error,
            expected="dma_stop() present in error-handling path",
            actual="present" if has_stop_near_error else "dma_stop missing from error path",
            check_type="constraint",
        )
    )

    return details
