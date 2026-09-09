"""Behavioral checks for multi-device PM ordering with rollback."""

import re

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis
from embedeval.check_utils import scoped_contains
from embedeval.check_utils import strip_comments


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
    # Three explicit calls and one loop over a three-device table are equally
    # correct; counting SUSPEND tokens punished the table form, which is the
    # better factoring. The table branch still requires three entries AND a
    # loop bound that covers them, so "suspend only two" stays detectable.
    stripped = strip_comments(generated_code)
    # Count actual suspend *calls*: a bare token count also counts the
    # `case PM_DEVICE_ACTION_SUSPEND:` label in the device's pm_action
    # handler, which inflated every submission by one and let a
    # two-device suspend reach the >= 3 threshold.
    suspend_call_count = len(
        re.findall(
            r"pm_device_action_run\s*\([^;]*PM_DEVICE_ACTION_SUSPEND", stripped
        )
    )
    table = re.search(r"\[\s*\w*\s*\]\s*=\s*\{([^}]*)\}", stripped)
    table_entries = (
        len(re.findall(r"\bdev_[a-zA-Z]\b", table.group(1))) if table else 0
    )
    loop_covers_table = bool(
        re.search(
            r"for\s*\([^;]*;\s*\w+\s*<\s*"
            r"(?:ARRAY_SIZE\s*\([^)]*\)|[A-Za-z_]\w*|[3-9]|\d{2,})\s*;",
            stripped,
        )
    )
    has_suspend_all = suspend_call_count >= 3 or (
        suspend_call_count >= 1 and table_entries >= 3 and loop_covers_table
    )
    details.append(
        CheckDetail(
            check_name="all_three_devices_suspended",
            passed=has_suspend_all,
            expected="All three devices suspended (three calls, or a loop over a three-device table)",
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
        scoped_contains(generated_code, '< 0', scope='code_only')
        and scoped_contains(generated_code, 'PM_DEVICE_ACTION_RESUME', scope='code_only')
        and scoped_contains(generated_code, 'PM_DEVICE_ACTION_SUSPEND', scope='code_only')
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
