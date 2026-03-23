"""Static analysis checks for watchdog with thread health monitoring application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate watchdog thread health monitoring code structure."""
    details: list[CheckDetail] = []

    # Check 1: Includes watchdog header
    has_wdt_h = "zephyr/drivers/watchdog.h" in generated_code
    details.append(
        CheckDetail(
            check_name="watchdog_header_included",
            passed=has_wdt_h,
            expected="zephyr/drivers/watchdog.h included",
            actual="present" if has_wdt_h else "missing",
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

    # Check 3: worker_alive flag is declared volatile (AI failure: non-volatile shared flag)
    has_volatile_flag = "volatile" in generated_code and (
        "worker_alive" in generated_code or "alive" in generated_code.lower()
    )
    details.append(
        CheckDetail(
            check_name="health_flag_is_volatile",
            passed=has_volatile_flag,
            expected="Worker alive flag declared volatile for cross-thread visibility",
            actual="present" if has_volatile_flag else "missing - flag may not be volatile",
            check_type="constraint",
        )
    )

    # Check 4: Uses wdt_install_timeout
    has_install = "wdt_install_timeout" in generated_code
    details.append(
        CheckDetail(
            check_name="wdt_install_timeout_called",
            passed=has_install,
            expected="wdt_install_timeout() called",
            actual="present" if has_install else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Uses wdt_setup
    has_setup = "wdt_setup" in generated_code
    details.append(
        CheckDetail(
            check_name="wdt_setup_called",
            passed=has_setup,
            expected="wdt_setup() called",
            actual="present" if has_setup else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: Uses worker thread (k_thread_create or K_THREAD_DEFINE)
    has_thread = (
        "k_thread_create" in generated_code or "K_THREAD_DEFINE" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="worker_thread_created",
            passed=has_thread,
            expected="Worker thread created with k_thread_create or K_THREAD_DEFINE",
            actual="present" if has_thread else "missing",
            check_type="exact_match",
        )
    )

    return details
