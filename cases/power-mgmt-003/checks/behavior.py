"""Behavioral checks for PM device with state tracking."""

import re

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate PM state tracking behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: State variable checked before transition (not just assigned)
    # (LLM failure: assigning new state without reading old state first)
    has_state_check = bool(
        re.search(
            r"(if\s*\([^)]*state[^)]*\)|if\s*\([^)]*suspend[^)]*\)|"
            r"if\s*\([^)]*active[^)]*\))",
            generated_code,
            re.IGNORECASE,
        )
    )
    details.append(
        CheckDetail(
            check_name="state_checked_before_transition",
            passed=has_state_check,
            expected="State variable checked (if statement) before applying transition",
            actual="present" if has_state_check else "missing",
            check_type="constraint",
        )
    )

    # Check 2: -EALREADY returned for duplicate suspend
    # (LLM failure: accepting duplicate suspend and returning 0)
    has_ealready = "EALREADY" in generated_code
    details.append(
        CheckDetail(
            check_name="ealready_returned_for_duplicate",
            passed=has_ealready,
            expected="-EALREADY returned for duplicate transitions",
            actual="present" if has_ealready else "missing (duplicate silently accepted)",
            check_type="constraint",
        )
    )

    # Check 3: Both SUSPEND and RESUME paths update state variable
    # (LLM failure: only SUSPEND updates state, RESUME does not)
    suspend_updates = bool(
        re.search(
            r"SUSPEND.*?(?:state|suspended|active)\s*=",
            generated_code,
            re.DOTALL | re.IGNORECASE,
        )
    )
    resume_updates = bool(
        re.search(
            r"RESUME.*?(?:state|suspended|active)\s*=",
            generated_code,
            re.DOTALL | re.IGNORECASE,
        )
    )
    both_update_state = suspend_updates and resume_updates
    details.append(
        CheckDetail(
            check_name="both_transitions_update_state",
            passed=both_update_state,
            expected="Both SUSPEND and RESUME update the state variable",
            actual=f"suspend_updates={suspend_updates}, resume_updates={resume_updates}",
            check_type="constraint",
        )
    )

    # Check 4: -ENOTSUP returned for unknown actions
    # (LLM failure: no default case, unknown actions silently return 0)
    has_enotsup = "ENOTSUP" in generated_code
    details.append(
        CheckDetail(
            check_name="enotsup_for_unknown_actions",
            passed=has_enotsup,
            expected="-ENOTSUP returned for unrecognized actions",
            actual="present" if has_enotsup else "missing",
            check_type="constraint",
        )
    )

    # Check 5: Callback called twice for same action (duplicate test in main)
    # (LLM failure: only calling suspend once, never testing the duplicate path)
    suspend_call_count = generated_code.count("PM_DEVICE_ACTION_SUSPEND")
    duplicate_tested = suspend_call_count >= 2
    details.append(
        CheckDetail(
            check_name="duplicate_transition_tested",
            passed=duplicate_tested,
            expected="PM_DEVICE_ACTION_SUSPEND appears >= 2 times (definition + duplicate call test)",
            actual=f"suspend_references={suspend_call_count}",
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
