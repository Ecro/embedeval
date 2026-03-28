"""Static analysis checks for periodic control loop with deadline handling."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate periodic control loop code structure."""
    details: list[CheckDetail] = []

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

    has_thread = (
        "K_THREAD_DEFINE" in generated_code
        or "k_thread_create" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="thread_created",
            passed=has_thread,
            expected="Dedicated thread created for control loop",
            actual="present" if has_thread else "missing",
            check_type="exact_match",
        )
    )

    return details
