"""Behavioral checks for dma-011."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []

    has_device_ready = "device_is_ready" in generated_code
    details.append(
        CheckDetail(
            check_name="device_ready_check",
            passed=has_device_ready,
            expected="device_is_ready() called on DMA device",
            actual="present" if has_device_ready else "missing",
            check_type="constraint",
        )
    )

    return details
