"""Static analysis checks for PM device action handler."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate PM code structure and required elements."""
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

    # Check 2: PM action callback function
    has_pm_action = "pm_device_action" in generated_code
    details.append(
        CheckDetail(
            check_name="pm_action_callback",
            passed=has_pm_action,
            expected="PM action callback or enum used",
            actual="present" if has_pm_action else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: SUSPEND action referenced
    has_suspend = "PM_DEVICE_ACTION_SUSPEND" in generated_code
    details.append(
        CheckDetail(
            check_name="suspend_action",
            passed=has_suspend,
            expected="PM_DEVICE_ACTION_SUSPEND handled",
            actual="present" if has_suspend else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: RESUME action referenced
    has_resume = "PM_DEVICE_ACTION_RESUME" in generated_code
    details.append(
        CheckDetail(
            check_name="resume_action",
            passed=has_resume,
            expected="PM_DEVICE_ACTION_RESUME handled",
            actual="present" if has_resume else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Uses switch or if-else for action dispatch
    has_switch = "switch" in generated_code or (
        "if" in generated_code and "action" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="action_dispatch",
            passed=has_switch,
            expected="switch or if-else on action parameter",
            actual="present" if has_switch else "missing",
            check_type="exact_match",
        )
    )

    return details
