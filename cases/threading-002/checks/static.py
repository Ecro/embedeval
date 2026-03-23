"""Static analysis checks for mutex-protected shared counter."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate mutex counter code structure and required elements."""
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

    # Check 2: Mutex defined (K_MUTEX_DEFINE or struct k_mutex)
    has_mutex_define = "K_MUTEX_DEFINE" in generated_code
    has_mutex_struct = "struct k_mutex" in generated_code
    has_mutex = has_mutex_define or has_mutex_struct
    details.append(
        CheckDetail(
            check_name="mutex_defined",
            passed=has_mutex,
            expected="K_MUTEX_DEFINE or struct k_mutex declared",
            actual="present" if has_mutex else "missing",
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

    # Check 5: Shared counter (global variable)
    has_counter = (
        "uint32_t" in generated_code
        or "int" in generated_code
    ) and (
        "counter" in generated_code
        or "shared" in generated_code
        or "count" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="shared_counter_declared",
            passed=has_counter,
            expected="Shared counter variable declared",
            actual="present" if has_counter else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: Two threads defined
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

    return details
