"""Static analysis checks for GPIO interrupt debounce with timer application."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate debounce code structure and required elements."""
    details: list[CheckDetail] = []

    # Check 1: Includes zephyr/drivers/gpio.h
    has_gpio_h = "zephyr/drivers/gpio.h" in generated_code
    details.append(
        CheckDetail(
            check_name="gpio_header_included",
            passed=has_gpio_h,
            expected="zephyr/drivers/gpio.h included",
            actual="present" if has_gpio_h else "missing",
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

    # Check 3: Uses k_timer (debounce mechanism)
    has_k_timer = "k_timer" in generated_code
    details.append(
        CheckDetail(
            check_name="uses_k_timer_for_debounce",
            passed=has_k_timer,
            expected="k_timer used for debounce",
            actual="present" if has_k_timer else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Hallucination check — gpio_debounce() does not exist in Zephyr
    has_fake_debounce = "gpio_debounce" in generated_code
    details.append(
        CheckDetail(
            check_name="no_gpio_debounce_hallucination",
            passed=not has_fake_debounce,
            expected="gpio_debounce() not used (does not exist in Zephyr)",
            actual="hallucinated API found" if has_fake_debounce else "clean",
            check_type="constraint",
        )
    )

    # Check 5: Hallucination check — GPIO_INT_DEBOUNCE flag does not exist
    has_fake_flag = "GPIO_INT_DEBOUNCE" in generated_code
    details.append(
        CheckDetail(
            check_name="no_gpio_int_debounce_flag",
            passed=not has_fake_flag,
            expected="GPIO_INT_DEBOUNCE flag not used (does not exist in Zephyr)",
            actual="hallucinated flag found" if has_fake_flag else "clean",
            check_type="constraint",
        )
    )

    # Check 6: Uses GPIO_DT_SPEC_GET
    has_dt_spec = "GPIO_DT_SPEC_GET" in generated_code
    details.append(
        CheckDetail(
            check_name="uses_dt_spec",
            passed=has_dt_spec,
            expected="GPIO_DT_SPEC_GET macro used",
            actual="present" if has_dt_spec else "missing",
            check_type="exact_match",
        )
    )

    # Check 7: No floating-point in file (use word-boundary regex on comment-stripped code)
    stripped = re.sub(r'//.*$', '', generated_code, flags=re.MULTILINE)
    stripped = re.sub(r'/\*.*?\*/', '', stripped, flags=re.DOTALL)
    stripped = re.sub(r'"[^"]*"', '""', stripped)
    fp_patterns = [r'\bfloat\b', r'\bdouble\b']
    has_float = any(re.search(p, stripped) for p in fp_patterns)
    details.append(
        CheckDetail(
            check_name="no_floating_point",
            passed=not has_float,
            expected="No floating-point types used",
            actual="floating-point found" if has_float else "clean",
            check_type="constraint",
        )
    )

    return details
