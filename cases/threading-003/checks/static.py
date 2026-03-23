"""Static analysis checks for semaphore-based event signaling."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate semaphore signaling code structure and required elements."""
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

    # Check 2: Semaphore defined
    has_sem_define = "K_SEM_DEFINE" in generated_code
    has_sem_init = "k_sem_init" in generated_code
    has_sem = has_sem_define or has_sem_init
    details.append(
        CheckDetail(
            check_name="semaphore_defined",
            passed=has_sem,
            expected="K_SEM_DEFINE or k_sem_init used",
            actual="present" if has_sem else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: k_sem_give called (producer)
    has_give = "k_sem_give" in generated_code
    details.append(
        CheckDetail(
            check_name="sem_give_called",
            passed=has_give,
            expected="k_sem_give() called (producer signals event)",
            actual="present" if has_give else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: k_sem_take called (consumer)
    has_take = "k_sem_take" in generated_code
    details.append(
        CheckDetail(
            check_name="sem_take_called",
            passed=has_take,
            expected="k_sem_take() called (consumer waits for event)",
            actual="present" if has_take else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Two threads defined
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
