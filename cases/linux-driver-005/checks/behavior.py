"""Behavioral checks for Linux sysfs attribute driver."""

import re

from embedeval.check_utils import (
    extract_error_blocks,
    strip_comments,
)
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate sysfs attribute driver behavioral properties."""
    details: list[CheckDetail] = []

    stripped = strip_comments(generated_code)

    # Check 1: sysfs_remove_group called in remove
    has_remove_group = "sysfs_remove_group" in generated_code
    details.append(
        CheckDetail(
            check_name="sysfs_remove_group_in_remove",
            passed=has_remove_group,
            expected="sysfs_remove_group() called in remove to match create",
            actual="present" if has_remove_group else "MISSING (kernel warning on unload!)",
            check_type="constraint",
        )
    )

    # Check 2: show uses sysfs_emit (not sprintf or snprintf)
    has_sysfs_emit = "sysfs_emit" in generated_code
    has_raw_sprintf = "sprintf(" in generated_code and "sysfs_emit" not in generated_code
    details.append(
        CheckDetail(
            check_name="sysfs_emit_in_show",
            passed=has_sysfs_emit and not has_raw_sprintf,
            expected="sysfs_emit() used in show (safe, bounds-checked)",
            actual="sysfs_emit present" if has_sysfs_emit else "missing (raw sprintf unsafe)",
            check_type="constraint",
        )
    )

    # Check 3: store uses kstrtoint or kstrtol (not sscanf or atoi)
    has_kstrtoint = (
        "kstrtoint" in generated_code
        or "kstrtol" in generated_code
        or "kstrtou" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="kstrtoint_in_store",
            passed=has_kstrtoint,
            expected="kstrtoint/kstrtol used in store (safe integer parsing)",
            actual="present" if has_kstrtoint else "missing (sscanf/atoi has no error return)",
            check_type="constraint",
        )
    )

    # Check 4: store returns count on success (not 0 or length)
    has_return_count = "return count" in generated_code
    details.append(
        CheckDetail(
            check_name="store_returns_count",
            passed=has_return_count,
            expected="store returns count on success (not 0)",
            actual="present" if has_return_count else "MISSING (infinite write loop!)",
            check_type="constraint",
        )
    )

    # Check 5: show output is newline-terminated (sysfs convention)
    has_newline = "\\n" in generated_code
    details.append(
        CheckDetail(
            check_name="show_newline_terminated",
            passed=has_newline,
            expected="show output contains \\n (sysfs convention)",
            actual="present" if has_newline else "missing (no newline in output)",
            check_type="constraint",
        )
    )

    # Check 6: attribute_group wired up to sysfs_create_group
    has_group_used = "sysfs_create_group" in generated_code and "attribute_group" in generated_code
    details.append(
        CheckDetail(
            check_name="attr_group_used_in_create",
            passed=has_group_used,
            expected="sysfs_create_group uses the attribute_group struct",
            actual="present" if has_group_used else "missing",
            check_type="constraint",
        )
    )

    # Check 7: sysfs_create_group error handled in probe
    # LLM failure: calling sysfs_create_group without checking return value
    error_blocks = extract_error_blocks(generated_code)
    has_group_err_handling = (
        "sysfs_create_group" in generated_code
        and ("return ret" in generated_code or bool(re.search(r'if\s*\(\s*ret\s*\)', generated_code)))
    )
    details.append(
        CheckDetail(
            check_name="sysfs_create_group_error_handled",
            passed=has_group_err_handling,
            expected="sysfs_create_group() return value checked and handled",
            actual="present" if has_group_err_handling else "sysfs_create_group failure may be ignored",
            check_type="constraint",
        )
    )

    # Check 8: No Zephyr API contamination
    zephyr_apis = ["k_work_submit", "k_thread_create", "K_THREAD_DEFINE",
                   "k_mutex_lock", "k_sleep("]
    has_zephyr = any(api in generated_code for api in zephyr_apis)
    details.append(
        CheckDetail(
            check_name="no_zephyr_apis",
            passed=not has_zephyr,
            expected="No Zephyr RTOS APIs in Linux sysfs driver",
            actual="clean" if not has_zephyr else "WRONG PLATFORM: Zephyr APIs found",
            check_type="constraint",
        )
    )

    return details
