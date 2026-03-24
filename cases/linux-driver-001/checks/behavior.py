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

    # Check 1: Uses copy_to_user (NOT raw pointer access)
    has_copy_to = "copy_to_user" in generated_code
    details.append(
        CheckDetail(
            check_name="copy_to_user_used",
            passed=has_copy_to,
            expected="copy_to_user() for kernel→user data transfer",
            actual="present" if has_copy_to else "MISSING (security!)",
            check_type="constraint",
        )
    )

    # Check 2: Uses copy_from_user (NOT raw pointer access)
    has_copy_from = "copy_from_user" in generated_code
    details.append(
        CheckDetail(
            check_name="copy_from_user_used",
            passed=has_copy_from,
            expected="copy_from_user() for user→kernel data transfer",
            actual="present" if has_copy_from else "MISSING (security!)",
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

    # Check 7: Error path in init frees previously allocated resources
    # LLM failure: alloc_chrdev_region succeeds, cdev_add fails,
    # but unregister_chrdev_region is NOT called before returning error
    error_blocks = extract_error_blocks(generated_code)
    error_blocks_unregister = any(
        "unregister_chrdev_region" in block or "cdev_del" in block
        for block in error_blocks
    )
    details.append(
        CheckDetail(
            check_name="init_error_path_cleanup",
            passed=error_blocks_unregister,
            expected="cdev_del/unregister_chrdev_region called in init error paths",
            actual="cleanup in error paths" if error_blocks_unregister else "resource leak on init failure",
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
