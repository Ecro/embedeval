"""Behavioral checks for watchdog-fed-by-timer cascaded safety application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate cascaded safety behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: Timer period < WDT timeout
    # WDT max must be > timer period (in seconds)
    # Heuristic: find window.max value and timer period, compare
    import re
    wdt_max_match = re.search(r"window\.max\s*=\s*(\d+)", generated_code)
    timer_period_match = re.search(r"K_SECONDS\((\d+)\)", generated_code)
    period_ok = False
    if wdt_max_match and timer_period_match:
        wdt_max_ms = int(wdt_max_match.group(1))
        timer_period_s = int(timer_period_match.group(1))
        period_ok = (timer_period_s * 1000) < wdt_max_ms
    elif wdt_max_match and re.search(r"K_MSEC\((\d+)\)", generated_code):
        msec_match = re.search(r"K_MSEC\((\d+)\)", generated_code)
        if msec_match:
            wdt_max_ms = int(wdt_max_match.group(1))
            period_ok = int(msec_match.group(1)) < wdt_max_ms
    details.append(
        CheckDetail(
            check_name="timer_period_less_than_wdt_timeout",
            passed=period_ok,
            expected="Timer period < WDT window.max timeout",
            actual="satisfied" if period_ok else "period >= timeout or not determinable",
            check_type="constraint",
        )
    )

    # Check 2: wdt_install_timeout before wdt_setup
    install_pos = generated_code.find("wdt_install_timeout")
    setup_pos = generated_code.find("wdt_setup")
    order_ok = install_pos != -1 and setup_pos != -1 and install_pos < setup_pos
    details.append(
        CheckDetail(
            check_name="install_before_setup",
            passed=order_ok,
            expected="wdt_install_timeout called before wdt_setup",
            actual="correct order" if order_ok else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 3: wdt_setup before k_timer_start
    timer_start_pos = generated_code.find("k_timer_start")
    setup_before_timer = setup_pos != -1 and timer_start_pos != -1 and setup_pos < timer_start_pos
    details.append(
        CheckDetail(
            check_name="wdt_setup_before_timer_start",
            passed=setup_before_timer,
            expected="wdt_setup called before k_timer_start",
            actual="correct order" if setup_before_timer else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 4: WDT_FLAG_RESET_SOC used
    has_reset_flag = "WDT_FLAG_RESET_SOC" in generated_code
    details.append(
        CheckDetail(
            check_name="reset_soc_flag",
            passed=has_reset_flag,
            expected="WDT_FLAG_RESET_SOC used",
            actual="present" if has_reset_flag else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: device_is_ready check present
    has_ready = "device_is_ready" in generated_code
    details.append(
        CheckDetail(
            check_name="device_ready_check",
            passed=has_ready,
            expected="device_is_ready() called for WDT device",
            actual="present" if has_ready else "missing",
            check_type="constraint",
        )
    )

    # Check 6: Cross-platform — no FreeRTOS APIs
    has_freertos = any(
        p in generated_code for p in ["xTimerCreate", "vTaskDelay", "xTaskCreate"]
    )
    details.append(
        CheckDetail(
            check_name="no_freertos_apis",
            passed=not has_freertos,
            expected="No FreeRTOS APIs (wrong RTOS)",
            actual="FreeRTOS API found" if has_freertos else "clean",
            check_type="constraint",
        )
    )

    return details
