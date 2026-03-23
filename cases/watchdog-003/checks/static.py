"""Static analysis checks for watchdog with callback application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate watchdog callback code structure and required elements."""
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

    # Check 4: Assigns a non-NULL callback in wdt_timeout_cfg (AI failure: callback=NULL)
    has_callback_assigned = (
        ".callback" in generated_code
        and "NULL" not in generated_code.split(".callback")[1].split(",")[0].split(";")[0]
        if ".callback" in generated_code else False
    )
    details.append(
        CheckDetail(
            check_name="callback_assigned",
            passed=has_callback_assigned,
            expected="Non-NULL callback assigned in wdt_timeout_cfg",
            actual="assigned" if has_callback_assigned else "NULL or missing",
            check_type="constraint",
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

    # Check 6: Uses wdt_feed in a loop before stopping
    has_feed = "wdt_feed" in generated_code
    details.append(
        CheckDetail(
            check_name="wdt_feed_called",
            passed=has_feed,
            expected="wdt_feed() called in main loop",
            actual="present" if has_feed else "missing",
            check_type="exact_match",
        )
    )

    return details
