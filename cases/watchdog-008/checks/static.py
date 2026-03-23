"""Static analysis checks for watchdog disable attempt detection application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate that watchdog is never disabled after start."""
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

    # Check 2: wdt_disable() NOT called — this is the core safety rule
    has_wdt_disable = "wdt_disable" in generated_code
    details.append(
        CheckDetail(
            check_name="no_wdt_disable_called",
            passed=not has_wdt_disable,
            expected="wdt_disable() NOT called (watchdog must never be disabled)",
            actual="wdt_disable found — SAFETY VIOLATION" if has_wdt_disable else "clean",
            check_type="constraint",
        )
    )

    # Check 3: Only WDT_OPT_PAUSE_HALTED_BY_DBG used (not disabling flags)
    has_pause_dbg = "WDT_OPT_PAUSE_HALTED_BY_DBG" in generated_code
    # Check for dangerous WDT options that effectively disable it
    has_dangerous_opt = "WDT_OPT_PAUSE_IN_SLEEP" in generated_code
    details.append(
        CheckDetail(
            check_name="only_safe_wdt_options",
            passed=has_pause_dbg and not has_dangerous_opt,
            expected="WDT_OPT_PAUSE_HALTED_BY_DBG used (no dangerous disable options)",
            actual="safe" if (has_pause_dbg and not has_dangerous_opt) else "unsafe or missing",
            check_type="constraint",
        )
    )

    # Check 4: wdt_install_timeout called
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

    # Check 5: wdt_setup called
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

    # Check 6: wdt_feed called (watchdog actually fed)
    has_feed = "wdt_feed" in generated_code
    details.append(
        CheckDetail(
            check_name="wdt_feed_called",
            passed=has_feed,
            expected="wdt_feed() called to service the watchdog",
            actual="present" if has_feed else "missing",
            check_type="exact_match",
        )
    )

    return details
