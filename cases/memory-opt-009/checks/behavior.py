"""Behavioral checks for BUILD_ASSERT compile-time validation."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate BUILD_ASSERT behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: BUILD_ASSERT used (not runtime assert or if-statements)
    # (LLM failure: using if (sizeof(buf) < MIN) { error } which is runtime)
    has_build_assert = "BUILD_ASSERT" in generated_code
    details.append(
        CheckDetail(
            check_name="compile_time_not_runtime",
            passed=has_build_assert,
            expected="BUILD_ASSERT (compile time) not runtime assert() or if-check",
            actual="present" if has_build_assert else "MISSING (BUILD_ASSERT required)",
            check_type="constraint",
        )
    )

    # Check 2: Meaningful condition (not trivially true like BUILD_ASSERT(1))
    import re
    has_meaningful = bool(re.search(r'BUILD_ASSERT\s*\(\s*sizeof|BUILD_ASSERT\s*\(\s*offsetof', generated_code))
    details.append(
        CheckDetail(
            check_name="meaningful_assert_condition",
            passed=has_meaningful,
            expected="BUILD_ASSERT condition uses sizeof() or offsetof()",
            actual="present" if has_meaningful else "missing meaningful condition",
            check_type="constraint",
        )
    )

    # Check 3: Not using static_assert directly (use Zephyr macro)
    has_static_assert = "_Static_assert(" in generated_code or (
        "static_assert(" in generated_code and "BUILD_ASSERT" not in generated_code
    )
    details.append(
        CheckDetail(
            check_name="not_raw_static_assert",
            passed=not has_static_assert,
            expected="Zephyr BUILD_ASSERT used, not raw _Static_assert",
            actual="clean" if not has_static_assert else "uses raw _Static_assert instead of BUILD_ASSERT",
            check_type="constraint",
        )
    )

    # Check 4: At least two BUILD_ASSERT calls (validates multiple constraints)
    assert_count = generated_code.count("BUILD_ASSERT")
    details.append(
        CheckDetail(
            check_name="multiple_assertions",
            passed=assert_count >= 2,
            expected="At least 2 BUILD_ASSERT calls for different constraints",
            actual=f"{assert_count} BUILD_ASSERT(s) found",
            check_type="constraint",
        )
    )

    # Check 5: No runtime assert() for size validation
    has_runtime_assert = bool(re.search(r'\bassert\s*\(\s*sizeof', generated_code))
    details.append(
        CheckDetail(
            check_name="no_runtime_assert_for_size",
            passed=not has_runtime_assert,
            expected="No runtime assert() for size checks (use BUILD_ASSERT)",
            actual="clean" if not has_runtime_assert else "runtime assert for size found (should be compile-time)",
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
