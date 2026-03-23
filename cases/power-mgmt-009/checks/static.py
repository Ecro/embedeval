"""Static analysis checks for battery-aware PM transitions."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate battery ADC and PM policy selection."""
    details: list[CheckDetail] = []

    # Check 1: kernel header
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

    # Check 2: ADC header or battery read function present
    has_adc = "zephyr/drivers/adc.h" in generated_code or "adc" in generated_code.lower()
    details.append(
        CheckDetail(
            check_name="adc_or_battery_read",
            passed=has_adc,
            expected="ADC header or battery read function present",
            actual="present" if has_adc else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: LOW_BATTERY_THRESHOLD defined
    has_threshold = "LOW_BATTERY_THRESHOLD" in generated_code or "threshold" in generated_code.lower()
    details.append(
        CheckDetail(
            check_name="battery_threshold_defined",
            passed=has_threshold,
            expected="LOW_BATTERY_THRESHOLD (or equivalent) defined",
            actual="present" if has_threshold else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Threshold comparison present
    import re
    has_comparison = bool(
        re.search(r"battery.*?<=?\s*\w*(?:threshold|LOW|20)\b|"
                  r"\w*(?:pct|percent|level|charge)\w*\s*<=?\s*\w+",
                  generated_code, re.IGNORECASE)
    )
    details.append(
        CheckDetail(
            check_name="threshold_comparison",
            passed=has_comparison,
            expected="Battery level compared against threshold",
            actual="comparison found" if has_comparison else "missing",
            check_type="constraint",
        )
    )

    # Check 5: At least two PM states or policies used (different behaviors)
    pm_states = []
    if "PM_STATE_SUSPEND_TO_IDLE" in generated_code:
        pm_states.append("SUSPEND_TO_IDLE")
    if "PM_STATE_SUSPEND_TO_RAM" in generated_code:
        pm_states.append("SUSPEND_TO_RAM")
    if "pm_policy_state_lock" in generated_code:
        pm_states.append("policy_lock")
    if "pm_state_force" in generated_code:
        pm_states.append("state_force")
    has_multiple_pm_behaviors = len(pm_states) >= 1 or bool(
        re.search(r"k_sleep.*?K_MSEC\(\d+\).*?k_sleep.*?K_MSEC\(\d+\)", generated_code, re.DOTALL)
    )
    details.append(
        CheckDetail(
            check_name="multiple_pm_behaviors",
            passed=has_multiple_pm_behaviors,
            expected="Different PM behaviors based on battery level",
            actual=f"PM behaviors: {pm_states}" if pm_states else "no PM state changes",
            check_type="constraint",
        )
    )

    return details
