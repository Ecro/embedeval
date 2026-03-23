"""Static analysis checks for watchdog-fed-by-timer cascaded safety application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate cascaded safety code structure and required elements."""
    details: list[CheckDetail] = []

    # Check 1: Includes zephyr/drivers/watchdog.h
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

    # Check 3: Uses wdt_install_timeout
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

    # Check 4: Uses wdt_setup
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

    # Check 5: wdt_feed called in timer callback (not main loop)
    has_wdt_feed = "wdt_feed" in generated_code
    details.append(
        CheckDetail(
            check_name="wdt_feed_called",
            passed=has_wdt_feed,
            expected="wdt_feed() called (in timer callback)",
            actual="present" if has_wdt_feed else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: k_timer used (not a bare thread with k_sleep for feeding)
    has_k_timer = "k_timer" in generated_code
    details.append(
        CheckDetail(
            check_name="uses_k_timer_for_wdt_feed",
            passed=has_k_timer,
            expected="k_timer used to feed WDT periodically",
            actual="present" if has_k_timer else "missing",
            check_type="exact_match",
        )
    )

    return details
