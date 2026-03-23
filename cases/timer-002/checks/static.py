"""Static analysis checks for one-shot timer with work queue application."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate one-shot timer and work queue code structure."""
    details: list[CheckDetail] = []

    # Check 1: Includes zephyr/kernel.h
    has_kernel_h = "zephyr/kernel.h" in generated_code
    details.append(
        CheckDetail(
            check_name="kernel_header_included",
            passed=has_kernel_h,
            expected="zephyr/kernel.h included",
            actual="present" if has_kernel_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: Uses K_TIMER_DEFINE or k_timer_init
    has_timer_def = (
        "K_TIMER_DEFINE" in generated_code or "k_timer_init" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="timer_defined",
            passed=has_timer_def,
            expected="K_TIMER_DEFINE or k_timer_init used",
            actual="present" if has_timer_def else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: Uses k_work_init or K_WORK_DEFINE
    has_work_init = (
        "k_work_init" in generated_code or "K_WORK_DEFINE" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="work_item_initialized",
            passed=has_work_init,
            expected="k_work_init() or K_WORK_DEFINE used",
            actual="present" if has_work_init else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Uses k_work_submit
    has_submit = "k_work_submit" in generated_code
    details.append(
        CheckDetail(
            check_name="work_submitted",
            passed=has_submit,
            expected="k_work_submit() called",
            actual="present" if has_submit else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Uses k_timer_start
    has_timer_start = "k_timer_start" in generated_code
    details.append(
        CheckDetail(
            check_name="timer_started",
            passed=has_timer_start,
            expected="k_timer_start() called",
            actual="present" if has_timer_start else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: One-shot uses K_NO_WAIT for period (AI failure: using non-zero period)
    has_no_wait_period = "K_NO_WAIT" in generated_code
    details.append(
        CheckDetail(
            check_name="one_shot_period_no_wait",
            passed=has_no_wait_period,
            expected="K_NO_WAIT used as period for one-shot timer",
            actual="present" if has_no_wait_period else "missing - may use non-zero period",
            check_type="constraint",
        )
    )

    return details
