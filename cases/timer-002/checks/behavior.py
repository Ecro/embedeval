"""Behavioral checks for one-shot timer with work queue application."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate one-shot timer and work queue behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: Timer is truly one-shot - period argument is K_NO_WAIT
    # AI failure: using non-zero period like K_MSEC(1000) for both duration and period
    one_shot_pattern = re.search(
        r"k_timer_start\s*\([^,]+,[^,]+,\s*(K_NO_WAIT|0)\s*\)", generated_code
    )
    is_one_shot = one_shot_pattern is not None
    details.append(
        CheckDetail(
            check_name="timer_is_truly_one_shot",
            passed=is_one_shot,
            expected="k_timer_start period argument is K_NO_WAIT (one-shot)",
            actual="one-shot period" if is_one_shot else "non-zero period - timer will repeat",
            check_type="constraint",
        )
    )

    # Check 2: Work submitted from timer expiry, not from main (correct pattern)
    # Look for k_work_submit inside a function that is not main
    lines = generated_code.splitlines()
    in_main = False
    submit_in_expiry = False
    submit_in_main = False
    for line in lines:
        if re.search(r"\bint\s+main\s*\(", line):
            in_main = True
        if "k_work_submit" in line:
            if in_main:
                submit_in_main = True
            else:
                submit_in_expiry = True
    details.append(
        CheckDetail(
            check_name="work_submitted_from_expiry",
            passed=submit_in_expiry and not submit_in_main,
            expected="k_work_submit() called from timer expiry function, not main",
            actual=(
                "correct - in expiry" if (submit_in_expiry and not submit_in_main)
                else "incorrect - in main or missing"
            ),
            check_type="constraint",
        )
    )

    # Check 3: Timer expiry function does not block (no k_sleep, k_msleep in callback)
    # AI failure: blocking inside timer callback
    expiry_fn_match = re.search(
        r"void\s+\w+\s*\(\s*struct\s+k_timer\s*\*[^)]*\)\s*\{([^}]*)\}",
        generated_code,
        re.DOTALL,
    )
    expiry_body = expiry_fn_match.group(1) if expiry_fn_match else ""
    expiry_blocks = "k_sleep" in expiry_body or "k_msleep" in expiry_body
    details.append(
        CheckDetail(
            check_name="expiry_does_not_block",
            passed=not expiry_blocks,
            expected="Timer expiry function does not call k_sleep or k_msleep",
            actual="no blocking" if not expiry_blocks else "blocking call in expiry",
            check_type="constraint",
        )
    )

    # Check 4: Worker function has correct k_work signature
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

    # Check 5: Main sleeps after starting timer (not busy-wait)
    has_sleep_after_start = "k_sleep" in generated_code and "k_timer_start" in generated_code
    details.append(
        CheckDetail(
            check_name="main_sleeps_after_start",
            passed=has_sleep_after_start,
            expected="Main sleeps after starting timer (not busy-wait)",
            actual="present" if has_sleep_after_start else "missing",
            check_type="constraint",
        )
    )

    return details
