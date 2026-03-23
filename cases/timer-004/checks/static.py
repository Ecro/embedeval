"""Static analysis checks for delayed work item application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate delayable work item code structure and required elements."""
    details: list[CheckDetail] = []

    # Check 1: Includes zephyr/kernel.h
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

    # Check 2: Uses K_WORK_DELAYABLE_DEFINE or k_work_init_delayable
    has_delayable = (
        "K_WORK_DELAYABLE_DEFINE" in generated_code
        or "k_work_init_delayable" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="delayable_work_defined",
            passed=has_delayable,
            expected="K_WORK_DELAYABLE_DEFINE or k_work_init_delayable used",
            actual="present" if has_delayable else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: Uses k_work_schedule (not k_work_submit which ignores delay)
    has_schedule = "k_work_schedule" in generated_code
    details.append(
        CheckDetail(
            check_name="work_scheduled_not_submitted",
            passed=has_schedule,
            expected="k_work_schedule() called (not k_work_submit for delayed work)",
            actual="present" if has_schedule else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Uses K_MSEC for delay (AI failure: using raw integers or wrong macro)
    has_msec = "K_MSEC" in generated_code
    details.append(
        CheckDetail(
            check_name="uses_k_msec_macro",
            passed=has_msec,
            expected="K_MSEC() used for delay duration",
            actual="present" if has_msec else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Does NOT use k_work_submit (AI failure: submitting instead of scheduling)
    uses_bare_submit = "k_work_submit" in generated_code and "k_work_schedule" not in generated_code
    details.append(
        CheckDetail(
            check_name="no_bare_submit_for_delayed",
            passed=not uses_bare_submit,
            expected="k_work_submit() not used alone for delayed execution",
            actual="incorrect submit only" if uses_bare_submit else "correct",
            check_type="constraint",
        )
    )

    return details
