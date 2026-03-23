"""Static analysis checks for task watchdog application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate task watchdog code structure and required elements."""
    details: list[CheckDetail] = []

    # Check 1: Includes task_wdt header (AI failure: using wdt driver header instead)
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

    # Check 2: Includes kernel header
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

    # Check 3: Uses task_wdt_init
    has_init = "task_wdt_init" in generated_code
    details.append(
        CheckDetail(
            check_name="task_wdt_init_called",
            passed=has_init,
            expected="task_wdt_init() called",
            actual="present" if has_init else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Uses task_wdt_add
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

    # Check 5: Uses task_wdt_feed
    has_feed = "task_wdt_feed" in generated_code
    details.append(
        CheckDetail(
            check_name="task_wdt_feed_called",
            passed=has_feed,
            expected="task_wdt_feed() called periodically",
            actual="present" if has_feed else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: Uses k_thread_create or K_THREAD_DEFINE for worker thread
    has_thread = (
        "k_thread_create" in generated_code or "K_THREAD_DEFINE" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="worker_thread_created",
            passed=has_thread,
            expected="k_thread_create() or K_THREAD_DEFINE used for worker thread",
            actual="present" if has_thread else "missing",
            check_type="exact_match",
        )
    )

    return details
