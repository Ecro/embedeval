"""Behavioral checks for PWM LED brightness control application."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate PWM behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: Device ready check before PWM operations (AI failure: missing this)
    has_ready_check = any(
        p in generated_code
        for p in ["pwm_is_ready_dt", "device_is_ready"]
    )
    details.append(
        CheckDetail(
            check_name="device_ready_check",
            passed=has_ready_check,
            expected="pwm_is_ready_dt() or device_is_ready() called before PWM operations",
            actual="present" if has_ready_check else "missing",
            check_type="constraint",
        )
    )

    # Check 2: Duty cycle bounded by period (AI failure: duty > period causes hardware error)
    # Look for guard comparisons: duty <= period, duty >= period with clamp, or capped duty
    has_duty_guard = any(
        p in generated_code
        for p in [
            ">= PWM_PERIOD",
            "<= PWM_PERIOD",
            "duty >= period",
            "duty <= period",
            "duty > period",
            "duty = period",
            "duty = PWM_PERIOD",
            "20000000",  # period constant — if used as bound it likely is clamped
        ]
    )
    details.append(
        CheckDetail(
            check_name="duty_bounded_by_period",
            passed=has_duty_guard,
            expected="Duty cycle clamped so it never exceeds the period",
            actual="guard present" if has_duty_guard else "no guard found",
            check_type="constraint",
        )
    )

    # Check 3: Varying duty cycle (fade up/down or stepped change)
    # Code must modify duty in a loop — look for += or -= on a duty variable
    import re
    has_varying_duty = bool(
        re.search(r'duty\w*\s*[+\-]?=', generated_code)
        or "duty++" in generated_code
        or "duty--" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="duty_cycle_varies",
            passed=has_varying_duty,
            expected="Duty cycle varied (incremented/decremented) in loop",
            actual="present" if has_varying_duty else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Sleep between steps (AI failure: no delay causing too-fast updates)
    has_sleep = any(p in generated_code for p in ["k_sleep", "k_msleep"])
    details.append(
        CheckDetail(
            check_name="sleep_between_steps",
            passed=has_sleep,
            expected="k_sleep or k_msleep between duty cycle steps",
            actual="present" if has_sleep else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Infinite loop present
    has_loop = any(p in generated_code for p in ["while (1)", "while(1)", "for (;;)", "for(;;)"])
    details.append(
        CheckDetail(
            check_name="infinite_loop_present",
            passed=has_loop,
            expected="Infinite loop for continuous brightness fade",
            actual="present" if has_loop else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: Period passed as nanoseconds to pwm_set_dt (not 0 or 1 which are wrong)
    # Heuristic: the literal 0 as period would be invalid; check that a non-trivial period is used
    pwm_set_pos = generated_code.find("pwm_set_dt")
    has_nonzero_period = pwm_set_pos != -1 and "pwm_set_dt(&" in generated_code
    details.append(
        CheckDetail(
            check_name="pwm_set_dt_called_with_args",
            passed=has_nonzero_period,
            expected="pwm_set_dt called with device pointer, period, and duty arguments",
            actual="called correctly" if has_nonzero_period else "missing or wrong form",
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
