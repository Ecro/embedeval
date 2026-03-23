"""Static analysis checks for PM device with state tracking."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate PM state tracking code structure."""
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

    # Check 2: PM action callback
    has_pm_action = "pm_device_action" in generated_code
    details.append(
        CheckDetail(
            check_name="pm_action_callback",
            passed=has_pm_action,
            expected="PM action callback or enum referenced",
            actual="present" if has_pm_action else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: SUSPEND action handled
    has_suspend = "PM_DEVICE_ACTION_SUSPEND" in generated_code
    details.append(
        CheckDetail(
            check_name="suspend_action_handled",
            passed=has_suspend,
            expected="PM_DEVICE_ACTION_SUSPEND handled",
            actual="present" if has_suspend else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: RESUME action handled
    has_resume = "PM_DEVICE_ACTION_RESUME" in generated_code
    details.append(
        CheckDetail(
            check_name="resume_action_handled",
            passed=has_resume,
            expected="PM_DEVICE_ACTION_RESUME handled",
            actual="present" if has_resume else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: -EALREADY returned for duplicate transitions
    has_ealready = "EALREADY" in generated_code
    details.append(
        CheckDetail(
            check_name="ealready_error_code",
            passed=has_ealready,
            expected="-EALREADY returned for duplicate transitions",
            actual="present" if has_ealready else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: State tracking variable present
    has_state_var = (
        "suspended" in generated_code
        or "state" in generated_code
        or "active" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="state_tracking_variable",
            passed=has_state_var,
            expected="State tracking variable declared",
            actual="present" if has_state_var else "missing",
            check_type="exact_match",
        )
    )

    return details
