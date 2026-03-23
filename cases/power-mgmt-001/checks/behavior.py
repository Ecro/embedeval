"""Behavioral checks for PM device action handler."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate PM behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: Both SUSPEND and RESUME handled
    # (LLM failure: only handling one direction)
    has_suspend = "PM_DEVICE_ACTION_SUSPEND" in generated_code
    has_resume = "PM_DEVICE_ACTION_RESUME" in generated_code
    details.append(
        CheckDetail(
            check_name="both_transitions_handled",
            passed=has_suspend and has_resume,
            expected="Both SUSPEND and RESUME actions handled",
            actual=f"suspend={has_suspend}, resume={has_resume}",
            check_type="constraint",
        )
    )

    # Check 2: Default/unsupported action returns error
    # (LLM failure: no default case, silently succeeds for unknown actions)
    has_enotsup = "ENOTSUP" in generated_code
    has_default = "default" in generated_code or "else" in generated_code
    details.append(
        CheckDetail(
            check_name="unsupported_action_error",
            passed=has_enotsup or has_default,
            expected="Default case returns -ENOTSUP or error",
            actual=f"ENOTSUP={has_enotsup}, default={has_default}",
            check_type="constraint",
        )
    )

    # Check 3: Callback returns int (success = 0)
    has_return_0 = "return 0" in generated_code
    details.append(
        CheckDetail(
            check_name="callback_returns_zero_on_success",
            passed=has_return_0,
            expected="Callback returns 0 on successful action",
            actual="present" if has_return_0 else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: pm_device_action_run called (not just callback defined)
    has_run = "pm_device_action_run" in generated_code
    details.append(
        CheckDetail(
            check_name="pm_action_run_called",
            passed=has_run,
            expected="pm_device_action_run() called to exercise PM",
            actual="present" if has_run else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Error handling for pm_device_action_run return
    # (LLM failure: ignoring return value of PM API)
    has_ret_check = "< 0" in generated_code or "!= 0" in generated_code
    details.append(
        CheckDetail(
            check_name="pm_error_handling",
            passed=has_ret_check,
            expected="Error check on pm_device_action_run return",
            actual="present" if has_ret_check else "missing",
            check_type="constraint",
        )
    )

    return details
