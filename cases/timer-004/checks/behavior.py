"""Behavioral checks for delayed work item application."""

import re

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate delayed work item behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: Uses k_work_schedule with K_MSEC(500) exactly
    has_500ms_schedule = bool(
        re.search(r"k_work_schedule\s*\([^,]+,\s*K_MSEC\s*\(\s*500\s*\)\s*\)", generated_code)
    )
    details.append(
        CheckDetail(
            check_name="scheduled_with_500ms_delay",
            passed=has_500ms_schedule,
            expected="k_work_schedule() called with K_MSEC(500) delay",
            actual="correct" if has_500ms_schedule else "wrong delay or wrong function",
            check_type="exact_match",
        )
    )

    # Check 2: Worker function has correct k_work signature (struct k_work *)
    has_work_sig = bool(
        re.search(r"\w+\s*\(\s*struct\s+k_work\s*\*", generated_code)
    )
    details.append(
        CheckDetail(
            check_name="worker_function_signature",
            passed=has_work_sig,
            expected="Worker function takes struct k_work * parameter",
            actual="correct" if has_work_sig else "wrong signature",
            check_type="exact_match",
        )
    )

    # Check 3: k_work_schedule used (not k_work_submit which doesn't support delay)
    # AI failure: calling k_work_submit for a delayed work item
    uses_schedule = "k_work_schedule" in generated_code
    uses_submit_instead = (
        "k_work_submit" in generated_code and not uses_schedule
    )
    details.append(
        CheckDetail(
            check_name="schedule_not_submit_for_delay",
            passed=uses_schedule and not uses_submit_instead,
            expected="k_work_schedule() used (not k_work_submit) for delayed execution",
            actual=(
                "correct" if uses_schedule
                else "uses k_work_submit which does not support delay"
            ),
            check_type="constraint",
        )
    )

    # Check 4: K_WORK_DELAYABLE_DEFINE or k_work_init_delayable used (not K_WORK_DEFINE)
    # AI failure: defining work with K_WORK_DEFINE then trying to schedule with delay
    uses_delayable_define = (
        "K_WORK_DELAYABLE_DEFINE" in generated_code
        or "k_work_init_delayable" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="delayable_work_type_used",
            passed=uses_delayable_define,
            expected="K_WORK_DELAYABLE_DEFINE or k_work_init_delayable for delayable work",
            actual="correct" if uses_delayable_define else "wrong work type - not delayable",
            check_type="constraint",
        )
    )

    # Check 5: Main waits long enough for work to execute (sleeps >= 500ms)
    has_adequate_sleep = bool(
        re.search(r"k_sleep\s*\(\s*K_(?:MSEC\s*\(\s*[5-9]\d{2,}|SECONDS\s*\()", generated_code)
    )
    details.append(
        CheckDetail(
            check_name="main_waits_for_work",
            passed=has_adequate_sleep,
            expected="Main sleeps long enough for delayed work to execute",
            actual="present" if has_adequate_sleep else "sleep too short or missing",
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
