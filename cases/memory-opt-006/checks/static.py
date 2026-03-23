"""Static analysis checks for Zephyr stack overflow detection."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate stack overflow detection code structure."""
    details: list[CheckDetail] = []

    has_stack_info = "CONFIG_THREAD_STACK_INFO=y" in generated_code
    details.append(
        CheckDetail(
            check_name="config_thread_stack_info_enabled",
            passed=has_stack_info,
            expected="CONFIG_THREAD_STACK_INFO=y",
            actual="present" if has_stack_info else "missing",
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

    has_stack_space_get = "k_thread_stack_space_get" in generated_code
    details.append(
        CheckDetail(
            check_name="k_thread_stack_space_get_used",
            passed=has_stack_space_get,
            expected="k_thread_stack_space_get() called",
            actual="present" if has_stack_space_get else "missing",
            check_type="exact_match",
        )
    )

    has_threshold = (
        "threshold" in generated_code.lower()
        or "warn_threshold" in generated_code
        or "< 512" in generated_code
        or "< 256" in generated_code
        or "THRESHOLD" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="threshold_comparison",
            passed=has_threshold,
            expected="Threshold comparison for low stack warning",
            actual="present" if has_threshold else "missing",
            check_type="exact_match",
        )
    )

    return details
