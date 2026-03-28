"""Behavioral checks for Linux proc file driver."""

import re

from embedeval.check_utils import (check_no_cross_platform_apis,
    strip_comments,
)
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate proc file driver behavioral properties."""
    details: list[CheckDetail] = []

    stripped = strip_comments(generated_code)

    # Check 1: proc_remove or remove_proc_entry called in exit
    has_remove = (
        "proc_remove" in generated_code or "remove_proc_entry" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="proc_removed_on_exit",
            passed=has_remove,
            expected="proc_remove() or remove_proc_entry() called in module_exit",
            actual="present" if has_remove else "MISSING (proc entry leaks on unload!)",
            check_type="constraint",
        )
    )

    # Check 2: seq_printf used (NOT sprintf/snprintf to user buffer)
    has_seq_printf = "seq_printf" in generated_code
    details.append(
        CheckDetail(
            check_name="seq_printf_not_raw_sprintf",
            passed=has_seq_printf,
            expected="seq_printf() used (not raw sprintf to user buffer)",
            actual="present" if has_seq_printf else "MISSING (use seq_printf, not sprintf!)",
            check_type="constraint",
        )
    )

    # Check 3: single_open used (standard pattern for simple seq files)
    has_single_open = "single_open" in generated_code
    details.append(
        CheckDetail(
            check_name="single_open_used",
            passed=has_single_open,
            expected="single_open() used in open callback",
            actual="present" if has_single_open else "missing",
            check_type="constraint",
        )
    )

    # Check 4: proc_ops has proc_read = seq_read
    has_seq_read = "seq_read" in generated_code
    details.append(
        CheckDetail(
            check_name="seq_read_in_proc_ops",
            passed=has_seq_read,
            expected="proc_ops has .proc_read = seq_read",
            actual="present" if has_seq_read else "missing",
            check_type="constraint",
        )
    )

    # Check 5: proc_create result checked for NULL
    has_null_check = (
        "!entry" in generated_code
        or "== NULL" in generated_code
        or "IS_ERR" in generated_code
        or "ENOMEM" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="proc_create_result_checked",
            passed=has_null_check,
            expected="proc_create() return value checked for failure",
            actual="present" if has_null_check else "missing",
            check_type="constraint",
        )
    )

    # Check 6: show function uses seq_file parameter
    has_show_fn = "seq_file" in generated_code
    details.append(
        CheckDetail(
            check_name="show_function_uses_seq_file",
            passed=has_show_fn,
            expected="show function takes struct seq_file* parameter",
            actual="present" if has_show_fn else "missing",
            check_type="constraint",
        )
    )

    # Check 7: proc_create failure handled by returning error from init
    # LLM failure: proc_create returns NULL but init proceeds and returns 0 anyway
    # Pattern: if (!entry) { return -ENOMEM; } — no braces or with braces
    proc_failure_handled = bool(
        re.search(r'if\s*\(\s*!\s*\w+\s*\)', generated_code)
        and ("return -ENOMEM" in generated_code or "return -" in generated_code)
    ) or bool(
        re.search(r'if\s*\(\s*!\s*\w+\s*\)\s*(?:\{[^}]*\}|[^;]+;)', generated_code)
    )
    details.append(
        CheckDetail(
            check_name="proc_create_failure_returns_error",
            passed=proc_failure_handled,
            expected="proc_create() failure causes init to return error",
            actual="present" if proc_failure_handled else "proc_create failure may be silently ignored",
            check_type="constraint",
        )
    )

    # Check 8: No Zephyr API contamination in Linux proc driver
    zephyr_apis = ["k_work_submit", "k_thread_create", "K_THREAD_DEFINE",
                   "k_mutex_lock", "k_sleep("]
    has_zephyr = any(api in generated_code for api in zephyr_apis)
    details.append(
        CheckDetail(
            check_name="no_zephyr_apis",
            passed=not has_zephyr,
            expected="No Zephyr RTOS APIs in Linux proc driver",
            actual="clean" if not has_zephyr else "WRONG PLATFORM: Zephyr APIs found",
            check_type="constraint",
        )
    )

    # Check: No cross-platform API contamination
    cross_plat = check_no_cross_platform_apis(generated_code, skip_platforms=["Linux_Userspace", "POSIX"])
    details.append(CheckDetail(
        check_name="no_cross_platform_apis",
        passed=len(cross_plat) == 0,
        expected="No FreeRTOS/Arduino/STM32_HAL APIs (Linux/POSIX is expected)",
        actual="clean" if not cross_plat else f"found: {[a for a, _ in cross_plat]}",
        check_type="constraint",
    ))

    return details
