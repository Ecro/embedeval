"""Static analysis checks for wake timer from deep sleep."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate wake timer and PM state force setup."""
    details: list[CheckDetail] = []

    # Check 1: PM header included
    has_pm_h = "zephyr/pm/pm.h" in generated_code or "zephyr/pm/device.h" in generated_code
    details.append(
        CheckDetail(
            check_name="pm_header_included",
            passed=has_pm_h,
            expected="zephyr/pm/pm.h included",
            actual="present" if has_pm_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: k_timer used for wakeup
    has_timer = "k_timer" in generated_code
    details.append(
        CheckDetail(
            check_name="k_timer_declared",
            passed=has_timer,
            expected="k_timer declared for wakeup alarm",
            actual="present" if has_timer else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: pm_state_force used (not k_sleep)
    has_pm_force = "pm_state_force" in generated_code
    details.append(
        CheckDetail(
            check_name="pm_state_force_used",
            passed=has_pm_force,
            expected="pm_state_force() used to enter deep sleep",
            actual="present" if has_pm_force else "missing (k_sleep? not deep sleep)",
            check_type="exact_match",
        )
    )

    # Check 4: PM_STATE_SUSPEND_TO_RAM used
    has_state = "PM_STATE_SUSPEND_TO_RAM" in generated_code
    details.append(
        CheckDetail(
            check_name="suspend_to_ram_state",
            passed=has_state,
            expected="PM_STATE_SUSPEND_TO_RAM used for deep sleep",
            actual="present" if has_state else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: WAKEUP_TIMER_MS < SLEEP_DURATION_MS
    wakeup_match = re.search(r"#define\s+WAKEUP_TIMER_MS\s+(\d+)", generated_code)
    sleep_match = re.search(r"#define\s+SLEEP_DURATION_MS\s+(\d+)", generated_code)
    timer_less_than_sleep = True
    if wakeup_match and sleep_match:
        wakeup_val = int(wakeup_match.group(1))
        sleep_val = int(sleep_match.group(1))
        timer_less_than_sleep = wakeup_val < sleep_val
    details.append(
        CheckDetail(
            check_name="wakeup_less_than_sleep_duration",
            passed=timer_less_than_sleep,
            expected="WAKEUP_TIMER_MS < SLEEP_DURATION_MS",
            actual=f"wakeup={wakeup_match.group(1) if wakeup_match else '?'} sleep={sleep_match.group(1) if sleep_match else '?'}",
            check_type="constraint",
        )
    )

    return details
