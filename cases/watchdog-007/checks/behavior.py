"""Behavioral checks for multi-thread watchdog monitoring application."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate multi-thread WDT behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: All 3 thread flags set before wdt_feed (supervisor checks all)
    # Heuristic: atomic_get or atomic_set count >= 3 (one per thread)
    atomic_set_count = generated_code.count("atomic_set")
    all_threads_report = atomic_set_count >= 3
    details.append(
        CheckDetail(
            check_name="all_threads_set_flags",
            passed=all_threads_report,
            expected="atomic_set called at least 3 times (one per worker thread)",
            actual=f"atomic_set called {atomic_set_count} time(s)",
            check_type="constraint",
        )
    )

    # Check 2: wdt_feed called only after checking all flags (supervisor feeds)
    # Heuristic: wdt_feed appears after atomic_get/atomic_clear in code
    wdt_feed_pos = generated_code.find("wdt_feed")
    atomic_check_pos = max(
        generated_code.find("atomic_get"),
        generated_code.find("atomic_clear"),
    )
    feed_after_check = wdt_feed_pos != -1 and atomic_check_pos != -1 and atomic_check_pos < wdt_feed_pos
    details.append(
        CheckDetail(
            check_name="wdt_feed_after_flag_check",
            passed=feed_after_check,
            expected="wdt_feed called after checking/clearing health flags",
            actual="correct order" if feed_after_check else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 3: K_THREAD_DEFINE or k_thread_create used for worker threads
    has_threads = "K_THREAD_DEFINE" in generated_code or "k_thread_create" in generated_code
    details.append(
        CheckDetail(
            check_name="threads_defined",
            passed=has_threads,
            expected="K_THREAD_DEFINE or k_thread_create used for worker threads",
            actual="present" if has_threads else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Supervisor checks ALL flags before feeding (conditional on all)
    # Check that the code has some && or conditional that covers all 3 flags
    has_all_check = (
        "&&" in generated_code
        or (generated_code.count("atomic_get") >= 3)
    )
    details.append(
        CheckDetail(
            check_name="supervisor_checks_all_flags",
            passed=has_all_check,
            expected="Supervisor checks all 3 flags (all-flag AND condition)",
            actual="present" if has_all_check else "missing — may only check some flags",
            check_type="constraint",
        )
    )

    # Check 5: device_is_ready check present
    has_ready = "device_is_ready" in generated_code
    details.append(
        CheckDetail(
            check_name="device_ready_check",
            passed=has_ready,
            expected="device_is_ready() called for WDT device",
            actual="present" if has_ready else "missing",
            check_type="constraint",
        )
    )

    # Check 6: Cross-platform — no FreeRTOS APIs
    has_freertos = any(
        p in generated_code for p in ["xTaskCreate", "vTaskDelay", "xQueueSend"]
    )
    details.append(
        CheckDetail(
            check_name="no_freertos_apis",
            passed=not has_freertos,
            expected="No FreeRTOS APIs (wrong RTOS)",
            actual="FreeRTOS API found" if has_freertos else "clean",
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
