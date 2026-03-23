"""Behavioral checks for PM device runtime enable/disable."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate PM runtime behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: pm_device_runtime_enable called before get/put
    # (LLM failure: calling get/put without enabling runtime PM first)
    enable_pos = generated_code.find("pm_device_runtime_enable")
    get_pos = generated_code.find("pm_device_runtime_get")
    enable_before_get = enable_pos >= 0 and get_pos >= 0 and enable_pos < get_pos
    details.append(
        CheckDetail(
            check_name="enable_before_get",
            passed=enable_before_get,
            expected="pm_device_runtime_enable() called before pm_device_runtime_get()",
            actual="correct order" if enable_before_get else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: Every get is paired with a put (no reference leak)
    # (LLM failure: calling get without put — device never suspends)
    get_count = generated_code.count("pm_device_runtime_get")
    put_count = generated_code.count("pm_device_runtime_put")
    get_put_balanced = get_count > 0 and put_count >= get_count
    details.append(
        CheckDetail(
            check_name="get_put_balanced",
            passed=get_put_balanced,
            expected="pm_device_runtime_put() called as many times as get() (no ref leak)",
            actual=f"get={get_count}, put={put_count}",
            check_type="constraint",
        )
    )

    # Check 3: Return values checked for enable/get/put
    # (LLM failure: ignoring error returns from runtime PM API)
    has_ret_check = "< 0" in generated_code or "!= 0" in generated_code
    details.append(
        CheckDetail(
            check_name="return_values_checked",
            passed=has_ret_check,
            expected="Return values of runtime PM calls checked for errors",
            actual="present" if has_ret_check else "missing",
            check_type="constraint",
        )
    )

    # Check 4: pm_device_runtime_disable called at end (cleanup)
    # (LLM failure: enabling runtime PM but never disabling it)
    has_disable = "pm_device_runtime_disable" in generated_code
    details.append(
        CheckDetail(
            check_name="runtime_pm_disabled_at_end",
            passed=has_disable,
            expected="pm_device_runtime_disable() called for cleanup",
            actual="present" if has_disable else "missing",
            check_type="constraint",
        )
    )

    # Check 5: SUSPEND and RESUME PM actions handled in callback
    # (LLM failure: PM callback only handles one direction)
    has_suspend_handled = "PM_DEVICE_ACTION_SUSPEND" in generated_code
    has_resume_handled = "PM_DEVICE_ACTION_RESUME" in generated_code
    details.append(
        CheckDetail(
            check_name="pm_callback_handles_both_directions",
            passed=has_suspend_handled and has_resume_handled,
            expected="PM callback handles both SUSPEND and RESUME",
            actual=f"suspend={has_suspend_handled}, resume={has_resume_handled}",
            check_type="constraint",
        )
    )

    return details
