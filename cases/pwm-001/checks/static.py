"""Static analysis checks for PWM LED brightness control application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate PWM code structure and required elements."""
    details: list[CheckDetail] = []

    # Check 1: Includes zephyr/drivers/pwm.h
    has_pwm_h = "zephyr/drivers/pwm.h" in generated_code
    details.append(
        CheckDetail(
            check_name="pwm_header_included",
            passed=has_pwm_h,
            expected="zephyr/drivers/pwm.h included",
            actual="present" if has_pwm_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: Includes zephyr/kernel.h
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

    # Check 3: Uses PWM DT spec macro to get device
    has_dt_spec = "PWM_DT_SPEC_GET" in generated_code
    details.append(
        CheckDetail(
            check_name="uses_pwm_dt_spec",
            passed=has_dt_spec,
            expected="PWM_DT_SPEC_GET macro used for devicetree binding",
            actual="present" if has_dt_spec else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Uses pwm_set_dt (AI failure: using raw pwm_set instead of DT variant)
    has_pwm_set_dt = "pwm_set_dt" in generated_code
    details.append(
        CheckDetail(
            check_name="uses_pwm_set_dt",
            passed=has_pwm_set_dt,
            expected="pwm_set_dt() called",
            actual="present" if has_pwm_set_dt else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Period defined in nanoseconds (not microseconds or milliseconds)
    # Correct values: 20000000 ns = 20 ms; heuristic — look for 8-digit number
    has_period_ns = any(
        p in generated_code
        for p in ["20000000", "PWM_MSEC(20)", "PWM_SEC(", "PWM_NSEC(20000000"]
    )
    details.append(
        CheckDetail(
            check_name="period_in_nanoseconds",
            passed=has_period_ns,
            expected="PWM period defined in nanoseconds (e.g. 20000000)",
            actual="present" if has_period_ns else "missing or wrong unit",
            check_type="exact_match",
        )
    )

    # Check 6: No raw register access
    has_raw_register = any(
        p in generated_code for p in ["volatile uint32_t", "*(uint32_t*)", "MMIO"]
    )
    details.append(
        CheckDetail(
            check_name="no_raw_register_access",
            passed=not has_raw_register,
            expected="Uses PWM API, not raw register access",
            actual="raw register found" if has_raw_register else "API only",
            check_type="constraint",
        )
    )

    return details
