"""Static analysis checks for system PM policy override."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate PM policy lock API usage."""
    details: list[CheckDetail] = []

    # Check 1: PM policy header
    has_pm_policy_h = "zephyr/pm/policy.h" in generated_code or "zephyr/pm/device.h" in generated_code
    details.append(
        CheckDetail(
            check_name="pm_policy_header",
            passed=has_pm_policy_h,
            expected="zephyr/pm/policy.h included",
            actual="present" if has_pm_policy_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: pm_policy_state_lock_get called
    has_lock_get = "pm_policy_state_lock_get" in generated_code
    details.append(
        CheckDetail(
            check_name="lock_get_called",
            passed=has_lock_get,
            expected="pm_policy_state_lock_get() called to prevent deep sleep",
            actual="present" if has_lock_get else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: pm_policy_state_lock_put called (no leak)
    has_lock_put = "pm_policy_state_lock_put" in generated_code
    details.append(
        CheckDetail(
            check_name="lock_put_called",
            passed=has_lock_put,
            expected="pm_policy_state_lock_put() called to release lock",
            actual="present" if has_lock_put else "missing (lock leaked!)",
            check_type="exact_match",
        )
    )

    # Check 4: PM_STATE_SUSPEND_TO_RAM referenced
    has_state = "PM_STATE_SUSPEND_TO_RAM" in generated_code
    details.append(
        CheckDetail(
            check_name="suspend_to_ram_state",
            passed=has_state,
            expected="PM_STATE_SUSPEND_TO_RAM used for deep sleep prevention",
            actual="present" if has_state else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Lock acquired before active period (get before put)
    get_pos = generated_code.find("pm_policy_state_lock_get")
    put_pos = generated_code.find("pm_policy_state_lock_put")
    get_before_put = get_pos != -1 and put_pos != -1 and get_pos < put_pos
    details.append(
        CheckDetail(
            check_name="lock_acquired_before_released",
            passed=get_before_put,
            expected="lock_get() appears before lock_put() in code",
            actual="correct order" if get_before_put else "wrong order or missing",
            check_type="constraint",
        )
    )

    return details
