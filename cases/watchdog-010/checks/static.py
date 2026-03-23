"""Static analysis checks for task watchdog main thread monitoring application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate task watchdog code structure and required elements."""
    details: list[CheckDetail] = []

    # Check 1: Includes zephyr/task_wdt/task_wdt.h
    has_task_wdt_h = "zephyr/task_wdt/task_wdt.h" in generated_code
    details.append(
        CheckDetail(
            check_name="task_wdt_header_included",
            passed=has_task_wdt_h,
            expected="zephyr/task_wdt/task_wdt.h included",
            actual="present" if has_task_wdt_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: Includes zephyr/kernel.h
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

    # Check 3: task_wdt_init called
    has_init = "task_wdt_init" in generated_code
    details.append(
        CheckDetail(
            check_name="task_wdt_init_called",
            passed=has_init,
            expected="task_wdt_init() called before task_wdt_add",
            actual="present" if has_init else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: task_wdt_add called
    has_add = "task_wdt_add" in generated_code
    details.append(
        CheckDetail(
            check_name="task_wdt_add_called",
            passed=has_add,
            expected="task_wdt_add() called to register channel",
            actual="present" if has_add else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: task_wdt_feed called
    has_feed = "task_wdt_feed" in generated_code
    details.append(
        CheckDetail(
            check_name="task_wdt_feed_called",
            passed=has_feed,
            expected="task_wdt_feed() called in main loop",
            actual="present" if has_feed else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: Uses k_sleep in loop (not a busy-wait)
    has_sleep = "k_sleep" in generated_code
    details.append(
        CheckDetail(
            check_name="uses_k_sleep",
            passed=has_sleep,
            expected="k_sleep() used between task_wdt_feed calls",
            actual="present" if has_sleep else "missing",
            check_type="constraint",
        )
    )

    return details
