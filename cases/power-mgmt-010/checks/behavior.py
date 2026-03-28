"""Behavioral checks for PM device state query before use."""

import re

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate device state check and conditional resume logic."""
    details: list[CheckDetail] = []

    # Check 1: safe_device_use (or equivalent) function defined
    has_safe_use = bool(
        re.search(r"\b(?:safe_device_use|device_safe_use|use_device_safe|check_and_use)\s*\(",
                  generated_code, re.IGNORECASE)
    )
    details.append(
        CheckDetail(
            check_name="safe_use_function_defined",
            passed=has_safe_use,
            expected="safe_device_use() or equivalent function defined",
            actual="present" if has_safe_use else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: Conditional resume — only resume if suspended
    # Pattern: if (state == PM_DEVICE_STATE_SUSPENDED) { ... resume ... }
    has_conditional_resume = bool(
        re.search(
            r"PM_DEVICE_STATE_SUSPENDED.*?PM_DEVICE_ACTION_RESUME|"
            r"if.*?suspended.*?resume",
            generated_code,
            re.DOTALL | re.IGNORECASE,
        )
    )
    details.append(
        CheckDetail(
            check_name="conditional_resume",
            passed=has_conditional_resume,
            expected="Resume called only if device is suspended",
            actual="conditional resume found" if has_conditional_resume else "no conditional resume",
            check_type="constraint",
        )
    )

    # Check 3: Device usage demonstrated after state check
    has_device_use = bool(
        re.search(r"Using device|device use|device_read|device_write",
                  generated_code, re.IGNORECASE)
    )
    details.append(
        CheckDetail(
            check_name="device_usage_demonstrated",
            passed=has_device_use,
            expected="Device usage shown after successful state check",
            actual="usage demonstrated" if has_device_use else "no device use shown",
            check_type="constraint",
        )
    )

    # Check 4: Return value from pm_device_state_get checked
    has_ret_check = bool(
        re.search(r"(?:ret|rc|err)\s*=\s*pm_device_state_get", generated_code)
    )
    details.append(
        CheckDetail(
            check_name="state_get_return_checked",
            passed=has_ret_check,
            expected="Return value of pm_device_state_get() checked for errors",
            actual="return check found" if has_ret_check else "return value ignored",
            check_type="constraint",
        )
    )

    # Check 5: Both states handled — suspended branch and active branch
    has_suspended_branch = "suspended" in generated_code.lower() or "PM_DEVICE_STATE_SUSPENDED" in generated_code
    has_active_branch = "active" in generated_code.lower() or "PM_DEVICE_STATE_ACTIVE" in generated_code
    details.append(
        CheckDetail(
            check_name="both_states_handled",
            passed=has_suspended_branch and has_active_branch,
            expected="Both suspended and active cases handled",
            actual=f"suspended={has_suspended_branch} active={has_active_branch}",
            check_type="constraint",
        )
    )

    # Check: No cross-platform API contamination
    cross_plat = check_no_cross_platform_apis(generated_code, skip_platforms=["Linux_Userspace"])
    details.append(CheckDetail(
        check_name="no_cross_platform_apis",
        passed=len(cross_plat) == 0,
        expected="No FreeRTOS/Arduino/STM32_HAL/POSIX APIs",
        actual="clean" if not cross_plat else f"found: {[a for a, _ in cross_plat]}",
        check_type="constraint",
    ))

    return details
