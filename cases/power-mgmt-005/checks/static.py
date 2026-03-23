"""Static analysis checks for multi-device PM ordering with rollback."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate multi-device PM code structure."""
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

    # Check 2: pm_device_action_run called
    has_action_run = "pm_device_action_run" in generated_code
    details.append(
        CheckDetail(
            check_name="pm_action_run_called",
            passed=has_action_run,
            expected="pm_device_action_run() called",
            actual="present" if has_action_run else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: SUSPEND action referenced
    has_suspend = "PM_DEVICE_ACTION_SUSPEND" in generated_code
    details.append(
        CheckDetail(
            check_name="suspend_action_used",
            passed=has_suspend,
            expected="PM_DEVICE_ACTION_SUSPEND referenced",
            actual="present" if has_suspend else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: RESUME action referenced (for rollback and resume_all)
    has_resume = "PM_DEVICE_ACTION_RESUME" in generated_code
    details.append(
        CheckDetail(
            check_name="resume_action_used",
            passed=has_resume,
            expected="PM_DEVICE_ACTION_RESUME referenced (rollback + resume)",
            actual="present" if has_resume else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: State tracking per device
    has_state = (
        "suspended" in generated_code
        or "state" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="per_device_state_tracking",
            passed=has_state,
            expected="Per-device state tracked (suspended flags or state array)",
            actual="present" if has_state else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: Rollback logic present
    has_rollback = generated_code.count("PM_DEVICE_ACTION_RESUME") >= 2
    details.append(
        CheckDetail(
            check_name="rollback_logic_present",
            passed=has_rollback,
            expected="RESUME used >= 2 times (rollback + resume_all)",
            actual=f"RESUME count={generated_code.count('PM_DEVICE_ACTION_RESUME')}",
            check_type="constraint",
        )
    )

    return details
