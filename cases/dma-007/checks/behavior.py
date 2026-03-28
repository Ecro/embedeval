"""Behavioral checks for DMA channel priority configuration."""

import re

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate DMA channel priority behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: Different priority values used (not same for both channels)
    priority_matches = re.findall(r"channel_priority\s*=\s*(\d+)", generated_code)
    if len(priority_matches) >= 2:
        priorities = [int(p) for p in priority_matches]
        different_priorities = len(set(priorities)) >= 2
    else:
        different_priorities = False
    details.append(
        CheckDetail(
            check_name="different_priority_values",
            passed=different_priorities,
            expected="Two channels configured with different priority values",
            actual=f"priorities found: {priority_matches}" if priority_matches else "priority values not found",
            check_type="constraint",
        )
    )

    # Check 2: Both channels configured before either is started
    # All dma_config calls should appear before dma_start calls
    last_config_pos = generated_code.rfind("dma_config(")
    first_start_pos = generated_code.find("dma_start(")
    configs_before_starts = (
        last_config_pos != -1
        and first_start_pos != -1
        and last_config_pos < first_start_pos
    )
    details.append(
        CheckDetail(
            check_name="both_channels_configured_before_start",
            passed=configs_before_starts,
            expected="All dma_config() calls before any dma_start() call",
            actual="correct order" if configs_before_starts else "wrong order — configure both before starting",
            check_type="constraint",
        )
    )

    # Check 3: Completion synchronization for both channels
    sem_count = generated_code.count("k_sem_take") + generated_code.count("K_SEM_DEFINE")
    has_dual_sync = sem_count >= 2
    details.append(
        CheckDetail(
            check_name="completion_sync_for_both_channels",
            passed=has_dual_sync,
            expected="Synchronization mechanism for both channel completions",
            actual=f"semaphore references={sem_count}",
            check_type="constraint",
        )
    )

    # Check 4: Verification of both destination buffers
    has_verify = generated_code.count("memcmp") >= 1 or (
        "OK" in generated_code and "DMA" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="both_buffers_verified",
            passed=has_verify,
            expected="DMA output verified (memcmp or success message)",
            actual="present" if has_verify else "missing verification",
            check_type="constraint",
        )
    )

    # Check 5: device_is_ready check
    has_ready = "device_is_ready" in generated_code
    details.append(
        CheckDetail(
            check_name="device_is_ready_check",
            passed=has_ready,
            expected="device_is_ready() called before DMA operations",
            actual="present" if has_ready else "missing",
            check_type="constraint",
        )
    )

    # Check: No cross-platform API contamination
    cross_plat = check_no_cross_platform_apis(generated_code, skip_platforms=["Linux_Userspace"])
    details.append(CheckDetail(
        check_name="no_cross_platform_apis",
        passed=len(cross_plat) == 0,
        expected="No FreeRTOS/Arduino/STM32_HAL/POSIX APIs",
        actual="clean" if not cross_plat else f"found: {[a for a, _ in cross_plat]}",
        check_type="constraint",
    ))

    return details
