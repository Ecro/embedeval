"""Static analysis checks for Linux workqueue driver."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate workqueue driver code structure."""
    details: list[CheckDetail] = []

    has_wq_h = "linux/workqueue.h" in generated_code
    details.append(
        CheckDetail(
            check_name="workqueue_header",
            passed=has_wq_h,
            expected="linux/workqueue.h included",
            actual="present" if has_wq_h else "missing",
            check_type="exact_match",
        )
    )

    has_work_struct = "work_struct" in generated_code
    details.append(
        CheckDetail(
            check_name="work_struct_defined",
            passed=has_work_struct,
            expected="struct work_struct embedded in device context",
            actual="present" if has_work_struct else "missing",
            check_type="exact_match",
        )
    )

    has_init_work = "INIT_WORK" in generated_code
    details.append(
        CheckDetail(
            check_name="init_work_called",
            passed=has_init_work,
            expected="INIT_WORK() called to initialize work struct",
            actual="present" if has_init_work else "MISSING (must call INIT_WORK before schedule_work!)",
            check_type="exact_match",
        )
    )

    has_schedule = "schedule_work" in generated_code
    details.append(
        CheckDetail(
            check_name="schedule_work_called",
            passed=has_schedule,
            expected="schedule_work() called to queue work item",
            actual="present" if has_schedule else "missing",
            check_type="exact_match",
        )
    )

    has_container_of = "container_of" in generated_code
    details.append(
        CheckDetail(
            check_name="container_of_in_handler",
            passed=has_container_of,
            expected="container_of() used to get parent struct in work handler",
            actual="present" if has_container_of else "missing",
            check_type="exact_match",
        )
    )

    return details
