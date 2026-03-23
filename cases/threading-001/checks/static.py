"""Static analysis checks for producer-consumer threading."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate threading code structure and required elements."""
    details: list[CheckDetail] = []

    # Check 1: kernel header
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

    # Check 2: Message queue defined
    has_msgq = (
        "K_MSGQ_DEFINE" in generated_code
        or "k_msgq_init" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="msgq_defined",
            passed=has_msgq,
            expected="K_MSGQ_DEFINE or k_msgq_init used",
            actual="present" if has_msgq else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: At least 2 threads defined
    thread_count = generated_code.count("K_THREAD_DEFINE")
    if thread_count < 2:
        thread_count += generated_code.count("k_thread_create")
    has_two_threads = thread_count >= 2
    details.append(
        CheckDetail(
            check_name="two_threads_defined",
            passed=has_two_threads,
            expected="At least 2 threads defined",
            actual=f"{thread_count} threads found",
            check_type="exact_match",
        )
    )

    # Check 4: k_msgq_put used (producer)
    has_put = "k_msgq_put" in generated_code
    details.append(
        CheckDetail(
            check_name="msgq_put_called",
            passed=has_put,
            expected="k_msgq_put() called (producer)",
            actual="present" if has_put else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: k_msgq_get used (consumer)
    has_get = "k_msgq_get" in generated_code
    details.append(
        CheckDetail(
            check_name="msgq_get_called",
            passed=has_get,
            expected="k_msgq_get() called (consumer)",
            actual="present" if has_get else "missing",
            check_type="exact_match",
        )
    )

    return details
