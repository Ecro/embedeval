"""Behavioral checks for multi-device PM ordering with rollback."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate multi-device PM ordering and rollback behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: Three devices referenced
    # (LLM failure: only two devices, missing the third dependency level)
    device_refs = len(
        set(re.findall(r"\bdev_[a-zA-Z]\b", generated_code))
    )
    has_three_devices = device_refs >= 3
    details.append(
        CheckDetail(
            check_name="three_devices_referenced",
            passed=has_three_devices,
            expected="Three devices referenced (dev_a, dev_b, dev_c or similar)",
            actual=f"device_refs={device_refs}",
            check_type="constraint",
        )
    )

    # Check 2: Suspend called for all three devices
    # (LLM failure: suspending only two of the three devices)
    suspend_call_count = generated_code.count("PM_DEVICE_ACTION_SUSPEND")
    has_suspend_all = suspend_call_count >= 3
    details.append(
        CheckDetail(
            check_name="all_three_devices_suspended",
            passed=has_suspend_all,
            expected="PM_DEVICE_ACTION_SUSPEND used >= 3 times (one per device)",
            actual=f"suspend_uses={suspend_call_count}",
            check_type="constraint",
        )
    )

    # Check 3: Resume called for all three devices (not just rollback path)
    # (LLM failure: resume_all only resumes one or two devices)
    resume_call_count = generated_code.count("PM_DEVICE_ACTION_RESUME")
    has_resume_all = resume_call_count >= 3
    details.append(
        CheckDetail(
            check_name="all_three_devices_resumed",
            passed=has_resume_all,
            expected="PM_DEVICE_ACTION_RESUME used >= 3 times (one per device + rollback)",
            actual=f"resume_uses={resume_call_count}",
            check_type="constraint",
        )
    )

    # Check 4: Error handling / rollback present (resume after failed suspend)
    # (LLM failure: no rollback — partial suspend leaves system in inconsistent state)
    has_rollback = bool(
        re.search(
            r"(rollback|roll.back|failed.*resume|resume.*failed|"
            r"if\s*\([^)]*ret[^)]*<\s*0[^)]*\)[^{]*\{[^}]*RESUME)",
            generated_code,
            re.IGNORECASE | re.DOTALL,
        )
    ) or (
        "< 0" in generated_code
        and "PM_DEVICE_ACTION_RESUME" in generated_code
        and "PM_DEVICE_ACTION_SUSPEND" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="rollback_on_failure",
            passed=has_rollback,
            expected="Rollback logic: resume already-suspended devices if a suspend fails",
            actual="present" if has_rollback else "missing (no rollback on partial failure)",
            check_type="constraint",
        )
    )

    # Check 5: State tracking per device checked before resume
    # (LLM failure: resuming devices that were never suspended — ignoring state)
    has_state_check_before_resume = bool(
        re.search(
            r"if\s*\([^)]*suspended[^)]*\)",
            generated_code,
            re.IGNORECASE,
        )
    ) or bool(
        re.search(
            r"if\s*\([^)]*state[^)]*\)",
            generated_code,
            re.IGNORECASE,
        )
    )
    details.append(
        CheckDetail(
            check_name="state_checked_before_resume",
            passed=has_state_check_before_resume,
            expected="Per-device state checked before resuming (no spurious resume)",
            actual="present" if has_state_check_before_resume else "missing",
            check_type="constraint",
        )
    )

    return details
