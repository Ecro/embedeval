"""Static analysis checks for thread pool with work queue completion tracking."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate work queue and semaphore completion tracking."""
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

    # Check 2: k_work array or multiple k_work items
    has_k_work = "k_work" in generated_code
    details.append(
        CheckDetail(
            check_name="k_work_declared",
            passed=has_k_work,
            expected="struct k_work declared for work items",
            actual="present" if has_k_work else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: k_sem declared for completion tracking
    has_sem = "k_sem" in generated_code
    details.append(
        CheckDetail(
            check_name="k_sem_for_completion",
            passed=has_sem,
            expected="k_sem declared for completion tracking",
            actual="present" if has_sem else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: k_work_init called (not just k_work_submit without init)
    has_init = "k_work_init" in generated_code
    details.append(
        CheckDetail(
            check_name="k_work_init_called",
            passed=has_init,
            expected="k_work_init() called before k_work_submit()",
            actual="present" if has_init else "missing (submit without init!)",
            check_type="exact_match",
        )
    )

    # Check 5: k_work_submit called
    has_submit = "k_work_submit" in generated_code
    details.append(
        CheckDetail(
            check_name="k_work_submit_called",
            passed=has_submit,
            expected="k_work_submit() called to enqueue work",
            actual="present" if has_submit else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: k_sem_give called (in work handler)
    has_give = "k_sem_give" in generated_code
    details.append(
        CheckDetail(
            check_name="k_sem_give_in_handler",
            passed=has_give,
            expected="k_sem_give() called in work handler for completion signal",
            actual="present" if has_give else "missing",
            check_type="exact_match",
        )
    )

    # Check 7: k_sem_take called (in main for waiting)
    has_take = "k_sem_take" in generated_code
    details.append(
        CheckDetail(
            check_name="k_sem_take_in_main",
            passed=has_take,
            expected="k_sem_take() called to wait for completion",
            actual="present" if has_take else "missing",
            check_type="exact_match",
        )
    )

    return details
