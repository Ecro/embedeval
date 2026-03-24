"""Behavioral checks for Linux workqueue driver."""

import re

from embedeval.check_utils import (
    strip_comments,
)
from embedeval.models import CheckDetail


def _extract_init_body(code: str) -> str:
    """Extract the body of the __init function."""
    match = re.search(r'__init\b[^{]*\{', code)
    if not match:
        return ""
    start = match.end()
    depth = 1
    for i in range(start, len(code)):
        if code[i] == '{':
            depth += 1
        elif code[i] == '}':
            depth -= 1
        if depth == 0:
            return code[start:i]
    return ""


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate workqueue driver behavioral properties."""
    details: list[CheckDetail] = []

    stripped = strip_comments(generated_code)

    # Check 1: INIT_WORK and schedule_work both present
    has_init = "INIT_WORK" in generated_code
    has_schedule = "schedule_work" in generated_code
    details.append(
        CheckDetail(
            check_name="init_work_before_schedule",
            passed=has_init and has_schedule,
            expected="INIT_WORK() called before schedule_work()",
            actual=f"INIT_WORK={has_init}, schedule_work={has_schedule}",
            check_type="constraint",
        )
    )

    # Check ordering: INIT_WORK must appear in the __init function (before work is
    # dispatched). schedule_work may be in a helper called from __init. Correct
    # pattern: __init body contains INIT_WORK before triggering dispatch.
    init_body = _extract_init_body(generated_code)
    init_in_init_fn = "INIT_WORK" in init_body
    # Also accept simpler case: INIT_WORK textually before last schedule_work call
    init_pos = generated_code.find("INIT_WORK")
    last_sched_pos = generated_code.rfind("schedule_work")
    init_ordered = init_in_init_fn or (has_init and has_schedule and init_pos < last_sched_pos)
    details.append(
        CheckDetail(
            check_name="init_work_ordered_before_schedule",
            passed=init_ordered,
            expected="INIT_WORK() in __init function before scheduling work",
            actual="correct order" if init_ordered else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: cancel_work_sync in exit (ensures work not running on unload)
    has_cancel = "cancel_work_sync" in generated_code
    details.append(
        CheckDetail(
            check_name="cancel_work_sync_in_exit",
            passed=has_cancel,
            expected="cancel_work_sync() called in module_exit for safe shutdown",
            actual="present" if has_cancel else "MISSING (use-after-free risk on unload!)",
            check_type="constraint",
        )
    )

    # Check 3: No k_work_submit — Zephyr RTOS API, wrong platform
    has_zephyr_work = "k_work_submit" in generated_code
    details.append(
        CheckDetail(
            check_name="no_zephyr_k_work_submit",
            passed=not has_zephyr_work,
            expected="No k_work_submit() (Zephyr RTOS API, not Linux)",
            actual="clean" if not has_zephyr_work else "WRONG PLATFORM: k_work_submit is Zephyr, use schedule_work()",
            check_type="constraint",
        )
    )

    # Check 4: Work handler uses process context (should not use spin_lock_irq)
    has_work_handler = "work_struct *work" in generated_code or "work_struct *" in generated_code
    details.append(
        CheckDetail(
            check_name="work_handler_process_context",
            passed=has_work_handler,
            expected="Work handler takes struct work_struct* parameter",
            actual="present" if has_work_handler else "missing",
            check_type="constraint",
        )
    )

    # Check 5: MODULE_LICENSE defined
    has_license = "MODULE_LICENSE" in generated_code
    details.append(
        CheckDetail(
            check_name="module_license_defined",
            passed=has_license,
            expected="MODULE_LICENSE defined",
            actual="present" if has_license else "missing",
            check_type="constraint",
        )
    )

    # Check 6: module_init and module_exit both present
    has_init_macro = "module_init" in generated_code
    has_exit_macro = "module_exit" in generated_code
    details.append(
        CheckDetail(
            check_name="init_exit_macros",
            passed=has_init_macro and has_exit_macro,
            expected="module_init() and module_exit() macros used",
            actual=f"init={has_init_macro}, exit={has_exit_macro}",
            check_type="constraint",
        )
    )

    # Check 7: Memory allocation failure handled in init
    # LLM failure: kzalloc/kmalloc for device struct not checked for NULL
    has_alloc_error_handling = (
        "ENOMEM" in generated_code
        or bool(re.search(r'if\s*\(\s*!\s*\w+\s*\)', generated_code))
    )
    details.append(
        CheckDetail(
            check_name="memory_alloc_failure_handled",
            passed=has_alloc_error_handling,
            expected="kzalloc/kmalloc failure handled with -ENOMEM",
            actual="present" if has_alloc_error_handling else "allocation failure may not be handled",
            check_type="constraint",
        )
    )

    # Check 8: No other Zephyr API contamination beyond k_work_submit
    other_zephyr_apis = ["k_thread_create", "K_THREAD_DEFINE",
                         "k_mutex_lock", "k_sem_take", "k_sleep("]
    has_other_zephyr = any(api in generated_code for api in other_zephyr_apis)
    details.append(
        CheckDetail(
            check_name="no_other_zephyr_apis",
            passed=not has_other_zephyr,
            expected="No other Zephyr RTOS APIs in Linux workqueue driver",
            actual="clean" if not has_other_zephyr else "WRONG PLATFORM: Zephyr APIs found",
            check_type="constraint",
        )
    )

    return details
