"""Static analysis checks for ISR stack protection."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate ISR data collection code structure."""
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

    has_semaphore = "k_sem" in generated_code
    details.append(
        CheckDetail(
            check_name="semaphore_used",
            passed=has_semaphore,
            expected="Semaphore for ISR-to-thread signaling",
            actual="present" if has_semaphore else "missing",
            check_type="exact_match",
        )
    )

    return details
