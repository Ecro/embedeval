"""Behavioral checks for battery-aware PM transitions."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate battery-aware PM behavioral correctness."""
    details: list[CheckDetail] = []

    # Check 1: Battery read happens before PM decision
    battery_read_pos = -1
    for fn_name in ["read_battery", "battery_percent", "adc_read", "get_battery"]:
        pos = generated_code.find(fn_name)
        if pos != -1:
            battery_read_pos = pos
            break
    pm_decision_pos = -1
    for pm_fn in ["apply_pm_policy", "pm_state_force", "pm_policy_state_lock", "k_sleep"]:
        pos = generated_code.find(pm_fn)
        if pos != -1:
            pm_decision_pos = pos
            break
    read_before_decision = battery_read_pos != -1 and pm_decision_pos != -1 and battery_read_pos < pm_decision_pos
    details.append(
        CheckDetail(
            check_name="battery_read_before_pm_decision",
            passed=read_before_decision,
            expected="Battery read before PM policy decision",
            actual="correct order" if read_before_decision else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: Low battery case uses more aggressive sleep
    has_low_batt_branch = bool(
        re.search(
            r"(aggressive|deep|suspend_to_ram|low.battery|LOW_BATTERY)",
            generated_code,
            re.IGNORECASE,
        )
    )
    details.append(
        CheckDetail(
            check_name="low_battery_aggressive_sleep",
            passed=has_low_batt_branch,
            expected="Low battery case uses aggressive sleep (longer sleep or deeper state)",
            actual="aggressive sleep branch found" if has_low_batt_branch else "no differentiation",
            check_type="constraint",
        )
    )

    # Check 3: Battery level printed in messages
    has_battery_msg = bool(
        re.search(r"battery|charge|percent|pct", generated_code, re.IGNORECASE)
    ) and "printk" in generated_code
    details.append(
        CheckDetail(
            check_name="battery_level_printed",
            passed=has_battery_msg,
            expected="Battery level printed in PM decision messages",
            actual="present" if has_battery_msg else "missing",
            check_type="constraint",
        )
    )

    # Check 4: apply_pm_policy (or equivalent) function defined
    has_policy_fn = bool(
        re.search(r"apply_pm_policy|set_pm_policy|adjust_pm|battery_pm", generated_code, re.IGNORECASE)
    )
    details.append(
        CheckDetail(
            check_name="pm_policy_function_defined",
            passed=has_policy_fn,
            expected="apply_pm_policy() or equivalent function defined",
            actual="present" if has_policy_fn else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Periodic battery check (loop with sleep)
    has_periodic = bool(
        re.search(r"while\s*\(\s*(?:1|true)\s*\).*?k_sleep|for\s*\([^)]*\).*?k_sleep",
                  generated_code, re.DOTALL)
    )
    details.append(
        CheckDetail(
            check_name="periodic_battery_check",
            passed=has_periodic,
            expected="Battery level checked periodically in a loop",
            actual="loop present" if has_periodic else "single check only",
            check_type="constraint",
        )
    )

    # Check 6: multiple PM states used (different sleep depths for different battery levels)
    # (LLM failure: single fixed sleep state regardless of battery level)
    pm_states = set(re.findall(r'PM_STATE_\w+', generated_code))
    details.append(CheckDetail(
        check_name="multiple_sleep_depths",
        passed=len(pm_states) >= 2,
        expected="At least 2 different PM states (adaptive power management)",
        actual=f"{len(pm_states)} PM states: {pm_states}" if pm_states else "no PM states found",
        check_type="constraint",
    ))

    return details
