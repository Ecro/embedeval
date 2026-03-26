"""Behavioral checks for Linux character device driver."""

import re

from embedeval.check_utils import (
    extract_error_blocks,
    strip_comments,
)
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Linux driver behavioral properties."""
    details: list[CheckDetail] = []

    stripped = strip_comments(generated_code)

    # Check 1: Uses copy_to_user (NOT raw pointer access).
    # Negative lookbehind excludes __copy_to_user (internal, non-validated variant).
    has_copy_to = bool(re.search(r'(?<!_)\bcopy_to_user\b', generated_code))
    details.append(
        CheckDetail(
            check_name="copy_to_user_used",
            passed=has_copy_to,
            expected="copy_to_user() for kernel→user data transfer",
            actual="present" if has_copy_to else "MISSING (security!) — __copy_to_user does not count",
            check_type="constraint",
        )
    )

    # Check 2: Uses copy_from_user (NOT raw pointer access).
    # Negative lookbehind excludes __copy_from_user (internal, non-validated variant).
    has_copy_from = bool(re.search(r'(?<!_)\bcopy_from_user\b', generated_code))
    details.append(
        CheckDetail(
            check_name="copy_from_user_used",
            passed=has_copy_from,
            expected="copy_from_user() for user→kernel data transfer",
            actual="present" if has_copy_from else "MISSING (security!) — __copy_from_user does not count",
            check_type="constraint",
        )
    )

    # Check 3: Cleanup in exit matches init resources
    has_register = (
        "alloc_chrdev_region" in generated_code
        or "register_chrdev" in generated_code
    )
    has_unregister = (
        "unregister_chrdev_region" in generated_code
        or "unregister_chrdev" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="register_unregister_balanced",
            passed=has_register and has_unregister,
            expected="chrdev registered in init AND unregistered in exit",
            actual=f"register={has_register}, unregister={has_unregister}",
            check_type="constraint",
        )
    )

    # Check 4: file_operations has .read and .write
    has_dot_read = ".read" in generated_code
    has_dot_write = ".write" in generated_code
    details.append(
        CheckDetail(
            check_name="fops_read_write",
            passed=has_dot_read and has_dot_write,
            expected="file_operations has .read and .write",
            actual=f"read={has_dot_read}, write={has_dot_write}",
            check_type="exact_match",
        )
    )

    # Check 5: .owner = THIS_MODULE (prevents module unload while in use)
    has_owner = "THIS_MODULE" in generated_code
    details.append(
        CheckDetail(
            check_name="this_module_owner",
            passed=has_owner,
            expected=".owner = THIS_MODULE in file_operations",
            actual="present" if has_owner else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: Error handling in init (rollback on failure)
    has_err_init = (
        "< 0" in generated_code or "IS_ERR" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="init_error_handling",
            passed=has_err_init,
            expected="Error handling with rollback in init",
            actual="present" if has_err_init else "missing",
            check_type="constraint",
        )
    )

    # Check 7: Error path in init frees ALL previously allocated resources.
    # LLM failure: partial cleanup — only calls cdev_del OR only calls
    # unregister_chrdev_region, leaving the other resource leaked.
    # Strategy: isolate the __init function body so that the exit function's
    # cleanup does not count.  Then verify BOTH symbols appear inside __init
    # (AND, not OR) — error blocks include IS_ERR() blocks which extract_error_blocks
    # does not match, so we check the full init body for both symbols.
    init_match = re.search(
        r'__init\s+\w+\s*\([^)]*\)\s*\{',
        generated_code,
    )
    if init_match:
        init_body_start = init_match.end()
        # Walk braces to find the matching close of the init function
        depth = 1
        pos = init_body_start
        while pos < len(generated_code) and depth > 0:
            if generated_code[pos] == '{':
                depth += 1
            elif generated_code[pos] == '}':
                depth -= 1
            pos += 1
        init_body = generated_code[init_body_start:pos]
        # Both cleanup calls must appear somewhere inside __init (covers both
        # `if (ret < 0)` blocks and `if (IS_ERR(...))` blocks).
        init_has_cdev_del = "cdev_del" in init_body
        init_has_unregister = "unregister_chrdev_region" in init_body
        cleanup_complete = init_has_cdev_del and init_has_unregister
        actual_cleanup = (
            "complete: both cdev_del and unregister_chrdev_region in __init"
            if cleanup_complete
            else (
                f"partial: cdev_del={init_has_cdev_del}, "
                f"unregister_chrdev_region={init_has_unregister} — resource leak on init failure"
            )
        )
    else:
        # Fallback when __init annotation is absent: require both in any error block
        error_blocks = extract_error_blocks(generated_code)
        init_has_cdev_del = any("cdev_del" in block for block in error_blocks)
        init_has_unregister = any("unregister_chrdev_region" in block for block in error_blocks)
        cleanup_complete = init_has_cdev_del and init_has_unregister
        actual_cleanup = (
            "complete cleanup (no __init marker)"
            if cleanup_complete
            else f"partial: cdev_del={init_has_cdev_del}, unregister_chrdev_region={init_has_unregister}"
        )
    details.append(
        CheckDetail(
            check_name="init_error_path_cleanup",
            passed=cleanup_complete,
            expected="BOTH cdev_del AND unregister_chrdev_region inside __init (full cleanup)",
            actual=actual_cleanup,
            check_type="constraint",
        )
    )

    # Check 8: No Zephyr API contamination in Linux driver code
    # LLM failure: mixing k_work_submit or k_thread_create into a Linux driver
    zephyr_apis = ["k_work_submit", "k_thread_create", "k_mutex_lock", "k_sem_take",
                   "K_THREAD_DEFINE", "k_sleep("]
    has_zephyr = any(api in generated_code for api in zephyr_apis)
    details.append(
        CheckDetail(
            check_name="no_zephyr_apis_in_linux_driver",
            passed=not has_zephyr,
            expected="No Zephyr RTOS APIs in Linux kernel driver",
            actual="clean" if not has_zephyr else "WRONG PLATFORM: Zephyr APIs in Linux driver",
            check_type="constraint",
        )
    )

    # Check 9: No deprecated gpio_request() — must use devm_gpiod_get if GPIO used
    has_gpio_request = "gpio_request(" in stripped
    details.append(
        CheckDetail(
            check_name="no_deprecated_gpio_request",
            passed=not has_gpio_request,
            expected="No deprecated gpio_request() (use devm_gpiod_get instead)",
            actual="clean" if not has_gpio_request else "deprecated gpio_request() found",
            check_type="constraint",
        )
    )

    return details
