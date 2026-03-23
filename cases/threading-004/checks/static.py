"""Static analysis checks for priority inheritance mutex."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate priority inheritance mutex code structure."""
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

    # Check 2: k_mutex used (not k_sem — only mutex provides priority inheritance)
    has_mutex = (
        "K_MUTEX_DEFINE" in generated_code
        or "struct k_mutex" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="mutex_used_not_semaphore",
            passed=has_mutex,
            expected="k_mutex used (provides priority inheritance)",
            actual="present" if has_mutex else "missing (k_sem has no priority inheritance)",
            check_type="exact_match",
        )
    )

    # Check 3: k_mutex_lock called
    has_lock = "k_mutex_lock" in generated_code
    details.append(
        CheckDetail(
            check_name="mutex_lock_called",
            passed=has_lock,
            expected="k_mutex_lock() called",
            actual="present" if has_lock else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: k_mutex_unlock called
    has_unlock = "k_mutex_unlock" in generated_code
    details.append(
        CheckDetail(
            check_name="mutex_unlock_called",
            passed=has_unlock,
            expected="k_mutex_unlock() called",
            actual="present" if has_unlock else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Three threads defined
    thread_count = generated_code.count("K_THREAD_DEFINE")
    if thread_count < 3:
        thread_count += generated_code.count("k_thread_create")
    has_three_threads = thread_count >= 3
    details.append(
        CheckDetail(
            check_name="three_threads_defined",
            passed=has_three_threads,
            expected="At least 3 threads defined (low, med, high priority)",
            actual=f"{thread_count} threads found",
            check_type="exact_match",
        )
    )

    return details
