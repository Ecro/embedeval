"""Behavioral checks for DMA transfer abort and error recovery."""

import re

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate DMA abort/recovery behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: dma_stop called (the key abort API — LLM must know this)
    has_dma_stop = "dma_stop" in generated_code
    details.append(
        CheckDetail(
            check_name="dma_stop_called",
            passed=has_dma_stop,
            expected="dma_stop() called to abort in-progress transfer",
            actual="present" if has_dma_stop else "missing — no abort mechanism",
            check_type="exact_match",
        )
    )

    # Check 2: dma_config called after dma_stop (reconfigure before retry)
    stop_pos = generated_code.find("dma_stop")
    # Find dma_config that appears AFTER dma_stop
    config_after_stop = False
    if stop_pos != -1:
        remaining = generated_code[stop_pos:]
        config_after_stop = "dma_config" in remaining
    details.append(
        CheckDetail(
            check_name="dma_config_after_stop",
            passed=config_after_stop,
            expected="dma_config() called after dma_stop() to reconfigure channel",
            actual="correct order"
            if config_after_stop
            else "missing reconfiguration after stop",
            check_type="constraint",
        )
    )

    # Check 3: Timeout mechanism present (k_sem_take with timeout OR k_poll OR timer)
    has_sem_timeout = bool(
        re.search(
            r"k_sem_take\s*\([^)]*K_MSEC|k_sem_take\s*\([^)]*K_SECONDS",
            generated_code,
        )
    )
    has_k_poll = "k_poll" in generated_code
    has_timer = "k_timer" in generated_code
    has_timeout = has_sem_timeout or has_k_poll or has_timer
    details.append(
        CheckDetail(
            check_name="timeout_mechanism_present",
            passed=has_timeout,
            expected="Timeout mechanism (k_sem_take with timeout, k_poll, or k_timer)",
            actual="present" if has_timeout else "missing — no timeout detection",
            check_type="constraint",
        )
    )

    # Check 4: Error/status checked in DMA callback or after operations
    has_status_check = bool(
        re.search(
            r"status\s*[!=<>]|status\s*==|err\s*[!=<>]|ret\s*[!=<>]|< 0",
            generated_code,
        )
    )
    details.append(
        CheckDetail(
            check_name="error_status_checked",
            passed=has_status_check,
            expected="Error/status checked after DMA operations or in callback",
            actual="present" if has_status_check else "missing — no error handling",
            check_type="constraint",
        )
    )

    # Check 5: Statistics tracking (counter variables for completions/timeouts)
    has_counter = bool(
        re.search(
            r"completion_count|timeout_count|abort_count|completions|timeouts|stats|"
            r"success_count|fail_count|retry_count|count\s*\+\+|count\s*\+=",
            generated_code,
        )
    )
    details.append(
        CheckDetail(
            check_name="statistics_tracking",
            passed=has_counter,
            expected="Transfer statistics tracked (completion/timeout/abort counts)",
            actual="present" if has_counter else "missing — no statistics tracking",
            check_type="constraint",
        )
    )

    # Check 6: dma_start called at least twice (initial + retry after abort)
    start_count = len(re.findall(r"dma_start\s*\(", generated_code))
    has_multiple_starts = start_count >= 2
    details.append(
        CheckDetail(
            check_name="dma_start_called_twice",
            passed=has_multiple_starts,
            expected="dma_start() called at least twice (initial + retry)",
            actual=f"dma_start called {start_count} time(s)",
            check_type="constraint",
        )
    )

    # Check 7: Transfer size of 256 bytes
    has_256 = bool(re.search(r"256|0x100", generated_code))
    details.append(
        CheckDetail(
            check_name="transfer_size_256",
            passed=has_256,
            expected="Transfer size of 256 bytes as specified",
            actual="present" if has_256 else "missing — wrong transfer size",
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
