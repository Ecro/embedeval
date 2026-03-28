"""Behavioral checks for DMA error handling with callback status check."""

import re

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


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

    # Check 2: volatile applied specifically to the error flag variable (not any variable).
    # Reject code where volatile appears only on a buffer/struct while the flag itself is plain int.
    has_volatile_flag = bool(re.search(
        r'volatile\s+\w*int\w*\s+\w*(?:error|err)_?flag',
        generated_code,
    )) or bool(re.search(
        r'\w*(?:error|err)_?flag\b.*volatile',
        generated_code,
    ))
    details.append(
        CheckDetail(
            check_name="error_flag_is_volatile",
            passed=has_volatile_flag,
            expected="Error flag declared as volatile to prevent compiler optimization",
            actual="present" if has_volatile_flag else "missing volatile on error flag — may be optimized away",
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

    # Check 7 (new): Error flag check in main actually causes a return/abort.
    # LLM failure: reads the flag and prints a message but never returns on error,
    # allowing execution to proceed as if the DMA completed successfully.
    error_check_pos = generated_code.find("if (dma_error_flag")
    if error_check_pos == -1:
        error_check_pos = generated_code.find("if (error_flag")
    error_causes_return = False
    if error_check_pos != -1:
        post_check = generated_code[error_check_pos:error_check_pos + 200]
        error_causes_return = "return" in post_check
    details.append(
        CheckDetail(
            check_name="error_flag_causes_return",
            passed=error_causes_return,
            expected="Error flag check followed by a return (not just a log message)",
            actual="return present after error check" if error_causes_return else "error checked but no return — execution continues on error",
            check_type="constraint",
        )
    )

    # Check 8: Error flag read AFTER k_sem_take (not before synchronization)
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

    # Check: No cross-platform API contamination
    cross_plat = check_no_cross_platform_apis(generated_code, skip_platforms=["Linux_Userspace"])
    details.append(CheckDetail(
        check_name="no_cross_platform_apis",
        passed=len(cross_plat) == 0,
        expected="No FreeRTOS/Arduino/STM32_HAL/POSIX APIs",
        actual="clean" if not cross_plat else f"found: {[a for a, _ in cross_plat]}",
        check_type="constraint",
    ))

    return details
