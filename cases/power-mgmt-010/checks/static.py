"""Static analysis checks for PM device state query before use."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate correct use of PM state query vs action enums."""
    details: list[CheckDetail] = []

    # Check 1: PM device header
    has_pm_h = "zephyr/pm/device.h" in generated_code
    details.append(
        CheckDetail(
            check_name="pm_device_header",
            passed=has_pm_h,
            expected="zephyr/pm/device.h included",
            actual="present" if has_pm_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: pm_device_state_get used for querying (not pm_device_action_run for query)
    has_state_get = "pm_device_state_get" in generated_code
    details.append(
        CheckDetail(
            check_name="pm_device_state_get_used",
            passed=has_state_get,
            expected="pm_device_state_get() used to query power state",
            actual="present" if has_state_get else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: PM_DEVICE_STATE_SUSPENDED used (state enum, not action enum)
    has_state_enum = "PM_DEVICE_STATE_SUSPENDED" in generated_code
    details.append(
        CheckDetail(
            check_name="pm_device_state_suspended_enum",
            passed=has_state_enum,
            expected="PM_DEVICE_STATE_SUSPENDED used (state enum, not action enum)",
            actual="present" if has_state_enum else "missing (confused with action?)",
            check_type="exact_match",
        )
    )

    # Check 4: PM_DEVICE_ACTION_RESUME used for actual resume (action enum)
    has_action_resume = "PM_DEVICE_ACTION_RESUME" in generated_code
    details.append(
        CheckDetail(
            check_name="pm_device_action_resume_used",
            passed=has_action_resume,
            expected="PM_DEVICE_ACTION_RESUME used for actual resume operation",
            actual="present" if has_action_resume else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: State checked BEFORE device use (not after)
    state_check_pos = generated_code.find("pm_device_state_get")
    use_pos = max(
        generated_code.find("Using device"),
        generated_code.find("use"),
    )
    state_before_use = state_check_pos != -1 and use_pos != -1 and state_check_pos < use_pos
    details.append(
        CheckDetail(
            check_name="state_checked_before_use",
            passed=state_before_use,
            expected="pm_device_state_get() called before device use",
            actual="correct order" if state_before_use else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 6: No confusing PM_DEVICE_ACTION_SUSPEND used as state check
    # LLM failure: using PM_DEVICE_ACTION_SUSPEND in comparison instead of PM_DEVICE_STATE_SUSPENDED
    confuses_action_as_state = bool(
        "== PM_DEVICE_ACTION_SUSPEND" in generated_code
        or "PM_DEVICE_ACTION_SUSPEND ==" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="no_action_enum_as_state",
            passed=not confuses_action_as_state,
            expected="No confusion: PM_DEVICE_ACTION_* not compared as state",
            actual="action used as state (BUG)" if confuses_action_as_state else "clean",
            check_type="constraint",
        )
    )

    return details
