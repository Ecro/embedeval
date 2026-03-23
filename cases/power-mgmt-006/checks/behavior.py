"""Behavioral checks for peripheral power gating."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate peripheral gating behavioral correctness."""
    details: list[CheckDetail] = []

    # Check 1: RESUME before use, SUSPEND after use (correct ordering)
    # Check global ordering: first RESUME must appear before last SUSPEND
    resume_pos = generated_code.find("PM_DEVICE_ACTION_RESUME")
    suspend_pos = generated_code.rfind("PM_DEVICE_ACTION_SUSPEND")
    correct_order = resume_pos != -1 and suspend_pos != -1 and resume_pos < suspend_pos
    details.append(
        CheckDetail(
            check_name="resume_before_suspend",
            passed=correct_order,
            expected="RESUME (enable) before access, SUSPEND (gate) after use",
            actual="correct order" if correct_order else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: State checked before RESUME (avoid double-resume)
    has_state_check_before_resume = bool(
        re.search(
            r"(if|while).*?(active|suspend|state).*?PM_DEVICE_ACTION_RESUME",
            generated_code,
            re.DOTALL,
        )
    )
    details.append(
        CheckDetail(
            check_name="state_checked_before_resume",
            passed=has_state_check_before_resume,
            expected="State checked before calling RESUME (avoid double-resume)",
            actual="check present" if has_state_check_before_resume else "no guard",
            check_type="constraint",
        )
    )

    # Check 3: Peripheral not accessed while suspended (no use after suspend without resume)
    # Heuristic: if printk "Using peripheral" appears, it should be between RESUME and SUSPEND
    has_use_msg = "Using peripheral" in generated_code or "peripheral" in generated_code.lower()
    details.append(
        CheckDetail(
            check_name="peripheral_used_while_active",
            passed=has_use_msg,
            expected="Peripheral usage shown between RESUME and SUSPEND",
            actual="usage message present" if has_use_msg else "no usage demonstration",
            check_type="constraint",
        )
    )

    # Check 4: Error return from pm_device_action_run checked
    has_error_check = bool(
        re.search(r"(ret|rc|err|result)\s*=\s*pm_device_action_run", generated_code)
    )
    details.append(
        CheckDetail(
            check_name="pm_action_return_checked",
            passed=has_error_check,
            expected="Return value of pm_device_action_run() checked",
            actual="return check found" if has_error_check else "return ignored",
            check_type="constraint",
        )
    )

    # Check 5: Periodic use demonstrated (k_sleep between uses)
    has_periodic = bool(re.search(r"k_sleep|k_msleep", generated_code))
    details.append(
        CheckDetail(
            check_name="periodic_use_demonstrated",
            passed=has_periodic,
            expected="Peripheral used periodically with sleep between uses",
            actual="sleep present" if has_periodic else "no sleep",
            check_type="constraint",
        )
    )

    return details
