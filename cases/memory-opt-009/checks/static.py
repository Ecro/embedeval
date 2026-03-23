"""Static analysis checks for BUILD_ASSERT compile-time validation."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate BUILD_ASSERT usage structure."""
    details: list[CheckDetail] = []

    has_build_assert = "BUILD_ASSERT" in generated_code
    details.append(
        CheckDetail(
            check_name="build_assert_used",
            passed=has_build_assert,
            expected="BUILD_ASSERT macro used",
            actual="present" if has_build_assert else "MISSING (use BUILD_ASSERT not runtime assert)",
            check_type="exact_match",
        )
    )

    has_sizeof = "sizeof(" in generated_code
    details.append(
        CheckDetail(
            check_name="sizeof_in_assert",
            passed=has_sizeof,
            expected="sizeof() used in BUILD_ASSERT condition",
            actual="present" if has_sizeof else "missing",
            check_type="exact_match",
        )
    )

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

    # Message string appears after BUILD_ASSERT somewhere as a string literal
    # Works for both same-line and multi-line BUILD_ASSERT calls
    has_message = bool(
        re.search(r'BUILD_ASSERT\b.*?,\s*"', generated_code, re.DOTALL)
    )
    details.append(
        CheckDetail(
            check_name="build_assert_has_message",
            passed=has_message,
            expected="BUILD_ASSERT has error message as second argument",
            actual="present" if has_message else "missing (message helps diagnose failures)",
            check_type="exact_match",
        )
    )

    return details
