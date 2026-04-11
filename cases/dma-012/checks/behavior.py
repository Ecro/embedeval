"""Behavioral checks for dma-010."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []

    has_device_ready = "device_is_ready" in generated_code
    details.append(
        CheckDetail(
            check_name="device_ready_check",
            passed=has_device_ready,
            expected="device_is_ready() called before using DMA device",
            actual="present" if has_device_ready else "missing",
            check_type="constraint",
        )
    )

    has_completion_wait = (
        "dma_done" in generated_code
        or "dma_callback" in generated_code
        or "k_sem" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="wait_for_completion",
            passed=has_completion_wait,
            expected="DMA completion signaled via callback / semaphore / done flag",
            actual="present" if has_completion_wait else "missing — fire-and-forget",
            check_type="constraint",
        )
    )

    return details
