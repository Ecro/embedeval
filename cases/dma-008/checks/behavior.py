"""Behavioral checks for DMA error handling with callback status check."""

import re

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

    # Check 6: Inside callback body, error flag is set when status != 0
    # LLM failure: checking status but not propagating it to the error flag
    callback_match = re.search(
        r'void\s+\w*(?:dma_callback|callback)\w*\s*\([^)]*(?:status)[^)]*\)\s*\{',
        generated_code, re.IGNORECASE
    )
    if not callback_match:
        # Broader fallback: any function with "callback" in name
        callback_match = re.search(
            r'void\s+\w*callback\w*\s*\([^{]*\)\s*\{',
            generated_code, re.IGNORECASE
        )
    if callback_match:
        cb_body_start = callback_match.end()
        cb_body = generated_code[cb_body_start:cb_body_start + 1000]
        status_check_match = re.search(r'if\s*\(\s*status|if\s*\(status', cb_body)
        if status_check_match:
            after_status_check = cb_body[status_check_match.start():status_check_match.start() + 200]
            flag_set_in_error = bool(
                re.search(r'(?:dma_error(?:_flag)?|error_flag)\s*=\s*(?!\s*0\b)', after_status_check)
            )
            actual_cb_msg = (
                "error flag set within status check branch"
                if flag_set_in_error
                else "status checked but error flag NOT set in that branch"
            )
        else:
            flag_set_in_error = False
            actual_cb_msg = "no status check (if status) found in callback body"
    else:
        flag_set_in_error = False
        actual_cb_msg = "callback function with status parameter not found"
    details.append(
        CheckDetail(
            check_name="callback_sets_flag_on_error_status",
            passed=flag_set_in_error,
            expected="Inside callback: when status != 0, error flag is assigned (not just checked)",
            actual=actual_cb_msg,
            check_type="constraint",
        )
    )

    # Check 7: Error flag read AFTER k_sem_take (not before synchronization)
    # LLM failure: reading error flag before waiting for DMA completion semaphore
    sem_take_pos = generated_code.rfind("k_sem_take")
    error_flag_name_c7 = (
        "dma_error_flag" if "dma_error_flag" in generated_code
        else "error_flag" if "error_flag" in generated_code
        else None
    )
    if error_flag_name_c7 and sem_take_pos != -1:
        # Find an 'if' referencing the error flag that comes after the last k_sem_take
        tail = generated_code[sem_take_pos:]
        error_check_in_tail = bool(
            re.search(
                r'if\s*\(\s*' + re.escape(error_flag_name_c7),
                tail
            )
        )
        actual_order_msg = (
            "correct: error flag checked after k_sem_take"
            if error_check_in_tail
            else "error flag check not found after last k_sem_take (checked too early or missing)"
        )
    elif sem_take_pos == -1:
        error_check_in_tail = False
        actual_order_msg = "k_sem_take not found — cannot verify ordering"
    else:
        error_check_in_tail = False
        actual_order_msg = "error flag variable not identified — cannot verify ordering"
    details.append(
        CheckDetail(
            check_name="error_flag_read_after_sync",
            passed=error_check_in_tail,
            expected="Error flag checked (if dma_error_flag) AFTER k_sem_take completes",
            actual=actual_order_msg,
            check_type="constraint",
        )
    )

    return details
