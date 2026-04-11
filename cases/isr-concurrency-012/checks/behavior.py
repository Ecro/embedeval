"""Behavioral checks for isr-concurrency-012."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []

    # Shared struct declared static (not on stack)
    has_shared_struct = (
        "static" in generated_code and "shared" in generated_code.lower()
    )
    details.append(
        CheckDetail(
            check_name="shared_state_static",
            passed=has_shared_struct,
            expected="Shared state in static storage, not on stack",
            actual="present" if has_shared_struct else "missing",
            check_type="constraint",
        )
    )

    has_worker_thread = (
        "k_thread_create" in generated_code or "K_THREAD_DEFINE" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="worker_thread_defined",
            passed=has_worker_thread,
            expected="Worker thread via k_thread_create or K_THREAD_DEFINE",
            actual="present" if has_worker_thread else "missing",
            check_type="constraint",
        )
    )

    return details
