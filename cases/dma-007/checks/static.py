"""Static analysis checks for DMA channel priority configuration."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate DMA channel priority code structure and required elements."""
    details: list[CheckDetail] = []

    # Check 1: DMA header included
    has_dma_h = "zephyr/drivers/dma.h" in generated_code
    details.append(
        CheckDetail(
            check_name="dma_header_included",
            passed=has_dma_h,
            expected="zephyr/drivers/dma.h included",
            actual="present" if has_dma_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: channel_priority field used
    has_priority = "channel_priority" in generated_code
    details.append(
        CheckDetail(
            check_name="channel_priority_field_used",
            passed=has_priority,
            expected="channel_priority field set in dma_config struct",
            actual="present" if has_priority else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: Two dma_config calls (one per channel)
    config_count = generated_code.count("dma_config(")
    has_two_configs = config_count >= 2
    details.append(
        CheckDetail(
            check_name="two_dma_config_calls",
            passed=has_two_configs,
            expected="dma_config() called at least twice (one per channel)",
            actual=f"dma_config calls={config_count}",
            check_type="constraint",
        )
    )

    # Check 4: Two dma_start calls
    start_count = generated_code.count("dma_start(")
    has_two_starts = start_count >= 2
    details.append(
        CheckDetail(
            check_name="two_dma_start_calls",
            passed=has_two_starts,
            expected="dma_start() called at least twice (one per channel)",
            actual=f"dma_start calls={start_count}",
            check_type="constraint",
        )
    )

    # Check 5: DEVICE_DT_GET present
    has_dev_get = "DEVICE_DT_GET" in generated_code
    details.append(
        CheckDetail(
            check_name="device_dt_get_present",
            passed=has_dev_get,
            expected="DEVICE_DT_GET used to obtain DMA device",
            actual="present" if has_dev_get else "missing",
            check_type="exact_match",
        )
    )

    return details
