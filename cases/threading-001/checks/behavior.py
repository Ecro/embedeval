"""Behavioral checks for producer-consumer threading."""

import re

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate threading behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: Producer and consumer have different priorities
    # (LLM failure: same priority for both threads)
    priority_matches = re.findall(
        r"K_THREAD_DEFINE\s*\([^,]+,\s*\d+,\s*\w+,"
        r"[^,]*,[^,]*,[^,]*,\s*(\d+)",
        generated_code,
    )
    if len(priority_matches) < 2:
        priority_matches = re.findall(
            r"\.prio\s*=\s*(\d+)|priority\s*[=,]\s*(\d+)",
            generated_code,
        )
        priority_matches = [
            m[0] or m[1] for m in priority_matches
        ]
    different_prio = (
        len(priority_matches) >= 2
        and len(set(priority_matches)) >= 2
    )
    details.append(
        CheckDetail(
            check_name="different_thread_priorities",
            passed=different_prio,
            expected="Producer and consumer have different priorities",
            actual=f"priorities: {priority_matches}",
            check_type="constraint",
        )
    )

    # Check 2: Producer sleeps between sends (not busy-loop)
    # (LLM failure: tight loop without sleep burns CPU)
    has_put = "k_msgq_put" in generated_code
    has_sleep_near_put = False
    if has_put:
        put_pos = generated_code.find("k_msgq_put")
        # Look for k_sleep within 300 chars after put
        nearby = generated_code[put_pos : put_pos + 300]
        has_sleep_near_put = "k_sleep" in nearby or "k_msleep" in nearby
    details.append(
        CheckDetail(
            check_name="producer_sleeps_between_sends",
            passed=has_sleep_near_put,
            expected="Producer calls k_sleep between sends",
            actual="present" if has_sleep_near_put else "missing",
            check_type="constraint",
        )
    )

    # Check 3: Consumer uses blocking get (K_FOREVER or timeout)
    has_blocking_get = (
        "K_FOREVER" in generated_code and "k_msgq_get" in generated_code
    ) or (
        "K_MSEC" in generated_code and "k_msgq_get" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="consumer_blocking_get",
            passed=has_blocking_get,
            expected="Consumer uses blocking k_msgq_get (K_FOREVER or timeout)",
            actual="present" if has_blocking_get else "missing or K_NO_WAIT",
            check_type="constraint",
        )
    )

    # Check 4: Message struct defined with data field
    has_struct = "struct" in generated_code
    has_data_field = bool(
        re.search(
            r"(?:u?int\d*_t|int|char|float|double|size_t|bool)\s+\w+",
            generated_code,
        )
    )
    details.append(
        CheckDetail(
            check_name="message_struct_with_data",
            passed=has_struct and has_data_field,
            expected="Message struct with typed data field",
            actual=f"struct={has_struct}, field={has_data_field}",
            check_type="exact_match",
        )
    )

    # Check 5: Queue capacity > 0
    cap_match = re.search(
        r"K_MSGQ_DEFINE\s*\(\s*\w+\s*,\s*[^,]+,\s*(\d+)",
        generated_code,
    )
    capacity_ok = False
    if cap_match:
        capacity_ok = int(cap_match.group(1)) > 0
    details.append(
        CheckDetail(
            check_name="queue_capacity_positive",
            passed=capacity_ok,
            expected="Message queue capacity > 0",
            actual=f"capacity={cap_match.group(1)}" if cap_match else "not found",
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
