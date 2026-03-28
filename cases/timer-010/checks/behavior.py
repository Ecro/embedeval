"""Behavioral checks for simple uptime counter application."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate uptime counter behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: k_uptime_get appears inside the loop (not just once at startup)
    loop_start = generated_code.find("while")
    uptime_pos = generated_code.find("k_uptime_get")
    uptime_in_loop = loop_start != -1 and uptime_pos != -1 and uptime_pos > loop_start
    details.append(
        CheckDetail(
            check_name="uptime_read_in_loop",
            passed=uptime_in_loop,
            expected="k_uptime_get() called inside the loop (not just once)",
            actual="inside loop" if uptime_in_loop else "missing or outside loop",
            check_type="constraint",
        )
    )

    # Check 2: Sleep is present in the loop (not a busy-wait)
    sleep_pos = generated_code.find("k_sleep")
    sleep_in_loop = loop_start != -1 and sleep_pos != -1 and sleep_pos > loop_start
    details.append(
        CheckDetail(
            check_name="sleep_in_loop",
            passed=sleep_in_loop,
            expected="k_sleep() called inside the loop",
            actual="inside loop" if sleep_in_loop else "missing or outside loop",
            check_type="constraint",
        )
    )

    # Check 3: printk used to output uptime
    has_printk = "printk" in generated_code
    details.append(
        CheckDetail(
            check_name="printk_used_for_output",
            passed=has_printk,
            expected="printk() used to output uptime value",
            actual="present" if has_printk else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: No custom uptime counter (should use k_uptime_get, not static int counter++)
    import re
    has_custom_counter = bool(
        re.search(r"static\s+(int|uint32_t|uint64_t)\s+\w+\s*=\s*0\s*;", generated_code)
        and "counter++" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="no_custom_uptime_counter",
            passed=not has_custom_counter,
            expected="No custom counter variable used as uptime substitute",
            actual="custom counter found" if has_custom_counter else "clean",
            check_type="constraint",
        )
    )

    # Check 5: Cross-platform — no FreeRTOS xTaskGetTickCount
    has_freertos_uptime = "xTaskGetTickCount" in generated_code or "pdTICKS_TO_MS" in generated_code
    details.append(
        CheckDetail(
            check_name="no_freertos_tick_count",
            passed=not has_freertos_uptime,
            expected="xTaskGetTickCount not used (FreeRTOS API, wrong RTOS)",
            actual="FreeRTOS API found" if has_freertos_uptime else "clean",
            check_type="constraint",
        )
    )

    # Check 6: Real-time — sleep duration is positive (not zero)
    has_zero_sleep = "K_MSEC(0)" in generated_code or "K_SECONDS(0)" in generated_code
    details.append(
        CheckDetail(
            check_name="sleep_duration_positive",
            passed=not has_zero_sleep,
            expected="Sleep duration is positive (avoids busy-wait with zero sleep)",
            actual="zero sleep found" if has_zero_sleep else "positive sleep",
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
