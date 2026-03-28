"""Behavioral checks for interrupt-driven character device driver."""

import re

from embedeval.check_utils import (check_no_cross_platform_apis,
    extract_error_blocks,
    strip_comments,
)
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate IRQ char device behavioral properties."""
    details: list[CheckDetail] = []

    stripped = strip_comments(generated_code)

    # Check 1: free_irq called in exit (balances request_irq in init)
    has_free_irq = "free_irq" in generated_code
    details.append(
        CheckDetail(
            check_name="free_irq_in_exit",
            passed=has_free_irq,
            expected="free_irq() called in module_exit to balance request_irq",
            actual="present" if has_free_irq else "MISSING (IRQ leak on unload!)",
            check_type="constraint",
        )
    )

    # Check 2: spin_lock used in IRQ handler (not mutex — mutex can sleep)
    has_spinlock = (
        "spin_lock" in generated_code
        or "DEFINE_SPINLOCK" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="spinlock_in_irq_handler",
            passed=has_spinlock,
            expected="spin_lock used in IRQ handler (mutex cannot be used in IRQ context)",
            actual="present" if has_spinlock else "MISSING or using mutex (sleep in IRQ!)",
            check_type="constraint",
        )
    )

    # Check 3: wait_event_interruptible used in read (blocks until IRQ fires)
    has_wait_event = "wait_event_interruptible" in generated_code
    details.append(
        CheckDetail(
            check_name="wait_event_interruptible_in_read",
            passed=has_wait_event,
            expected="wait_event_interruptible() in read() for blocking wait",
            actual="present" if has_wait_event else "missing (busy-poll or no wait?)",
            check_type="constraint",
        )
    )

    # Check 4: wake_up_interruptible called from IRQ handler
    has_wake_up = "wake_up_interruptible" in generated_code
    details.append(
        CheckDetail(
            check_name="wake_up_interruptible_in_handler",
            passed=has_wake_up,
            expected="wake_up_interruptible() called from IRQ handler",
            actual="present" if has_wake_up else "MISSING (reader never unblocks!)",
            check_type="constraint",
        )
    )

    # Check 5: IRQ_HANDLED returned from handler (not IRQ_NONE or 0)
    has_irq_handled = "IRQ_HANDLED" in generated_code
    details.append(
        CheckDetail(
            check_name="irq_handled_returned",
            passed=has_irq_handled,
            expected="IRQ_HANDLED returned from IRQ handler",
            actual="present" if has_irq_handled else "missing",
            check_type="constraint",
        )
    )

    # Check 6: copy_to_user used (not direct pointer access in read)
    has_copy_to = "copy_to_user" in generated_code
    details.append(
        CheckDetail(
            check_name="copy_to_user_in_read",
            passed=has_copy_to,
            expected="copy_to_user() for kernel→user transfer in read()",
            actual="present" if has_copy_to else "MISSING (security!)",
            check_type="constraint",
        )
    )

    # Check 7: Error path in init frees previously allocated resources
    # LLM failure: alloc_chrdev_region succeeds, request_irq fails,
    # but cdev_del/unregister_chrdev_region NOT called before returning error
    error_blocks = extract_error_blocks(generated_code)
    error_path_cleanup = any(
        "unregister_chrdev_region" in block or "cdev_del" in block
        for block in error_blocks
    )
    details.append(
        CheckDetail(
            check_name="init_error_path_cleanup",
            passed=error_path_cleanup,
            expected="cdev_del/unregister_chrdev_region in init error paths",
            actual="cleanup in error paths" if error_path_cleanup else "resource leak on init failure",
            check_type="constraint",
        )
    )

    # Check 8: No Zephyr API contamination in Linux IRQ driver
    zephyr_apis = ["k_work_submit", "k_thread_create", "K_THREAD_DEFINE",
                   "k_mutex_lock", "k_sleep(", "K_SPINLOCK_DEFINE"]
    has_zephyr = any(api in generated_code for api in zephyr_apis)
    details.append(
        CheckDetail(
            check_name="no_zephyr_apis",
            passed=not has_zephyr,
            expected="No Zephyr RTOS APIs in Linux IRQ driver",
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
