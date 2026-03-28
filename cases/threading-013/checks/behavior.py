"""Behavioral checks for shared memory IPC implementation."""

import re

from embedeval.check_utils import (
    check_no_cross_platform_apis,
    strip_comments,
)
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []
    stripped = strip_comments(generated_code)

    # Check 1: Shared memory struct defined with data + flag
    has_shared_struct = bool(re.search(
        r'struct\s+\w*(?:shared|ipc|shm)\w*\s*\{', stripped, re.IGNORECASE
    ))
    details.append(CheckDetail(
        check_name="shared_memory_struct",
        passed=has_shared_struct,
        expected="Shared memory struct defined with data and synchronization fields",
        actual="struct found" if has_shared_struct else "no shared memory struct",
        check_type="constraint",
    ))

    # Check 2: volatile or atomic on shared flag/data
    has_volatile_shared = bool(re.search(
        r'volatile\s+\w+\s+\w*(?:flag|ready|valid|new_data|status)', stripped, re.IGNORECASE
    )) or bool(re.search(
        r'atomic_t\s+\w*(?:flag|ready|valid|new_data|status)', stripped, re.IGNORECASE
    ))
    details.append(CheckDetail(
        check_name="volatile_on_shared_flags",
        passed=has_volatile_shared,
        expected="volatile or atomic_t on shared synchronization flag",
        actual="volatile/atomic found" if has_volatile_shared else "plain variable — compiler may cache, race condition",
        check_type="constraint",
    ))

    # Check 3: Producer-consumer handshake (flag set by producer, checked by consumer)
    has_flag_set = bool(re.search(r'(?:flag|ready|valid|new_data)\s*=\s*(?:1|true)', stripped, re.IGNORECASE))
    has_flag_check = bool(re.search(r'(?:while|if)\s*\([^)]*(?:flag|ready|valid|new_data)', stripped, re.IGNORECASE))
    details.append(CheckDetail(
        check_name="handshake_mechanism",
        passed=has_flag_set and has_flag_check,
        expected="Flag-based handshake: producer sets flag, consumer checks flag",
        actual=f"set={has_flag_set}, check={has_flag_check}",
        check_type="constraint",
    ))

    # Check 4: Consumer clears flag after reading (prevents re-read of stale data)
    has_flag_clear = bool(re.search(r'(?:flag|ready|valid|new_data)\s*=\s*(?:0|false)', stripped, re.IGNORECASE))
    details.append(CheckDetail(
        check_name="flag_cleared_after_read",
        passed=has_flag_clear,
        expected="Consumer clears flag after reading (acknowledges data consumed)",
        actual="flag cleared" if has_flag_clear else "flag never cleared — producer cannot detect consumption",
        check_type="constraint",
    ))

    # Check 5: Memory alignment on shared struct
    has_alignment = bool(re.search(
        r'__aligned|__attribute__\s*\(\s*\(\s*aligned', stripped
    )) or bool(re.search(
        r'__attribute__\s*\(\s*\(\s*section', stripped
    ))
    details.append(CheckDetail(
        check_name="shared_memory_aligned",
        passed=has_alignment,
        expected="Shared memory struct has alignment attribute (cache line or DMA safe)",
        actual="aligned" if has_alignment else "no alignment — possible cache line split or DMA issue",
        check_type="constraint",
    ))

    # Check 6: Data written BEFORE flag set (ordering correctness)
    # Find positions: data assignment should come before flag=1
    data_patterns = re.finditer(r'(?:data|value|sensor|payload|sample)\s*=', stripped, re.IGNORECASE)
    flag_set_match = re.search(r'(?:flag|ready|valid|new_data)\s*=\s*(?:1|true)', stripped, re.IGNORECASE)
    data_before_flag = False
    if flag_set_match:
        flag_pos = flag_set_match.start()
        for dm in data_patterns:
            if dm.start() < flag_pos:
                data_before_flag = True
                break
    details.append(CheckDetail(
        check_name="data_before_flag",
        passed=data_before_flag,
        expected="Data written before flag set (prevents consumer reading partial data)",
        actual="correct order" if data_before_flag else "flag may be set before data is fully written",
        check_type="constraint",
    ))

    # Check 7: Memory barrier between data write and flag set
    has_barrier = any(kw in stripped for kw in [
        "compiler_barrier", "__DSB", "__DMB", "barrier", "atomic_set",
        "k_smp_mb", "__sync_synchronize", "__COMPILER_BARRIER",
    ])
    details.append(CheckDetail(
        check_name="memory_barrier_present",
        passed=has_barrier,
        expected="Memory barrier between data write and flag set (prevents reordering)",
        actual="barrier found" if has_barrier else "no barrier — CPU/compiler may reorder writes",
        check_type="constraint",
    ))

    # Check 8: Two threads (producer + consumer)
    thread_count = len(re.findall(r'K_THREAD_DEFINE|k_thread_create', stripped))
    details.append(CheckDetail(
        check_name="two_threads_defined",
        passed=thread_count >= 2,
        expected="At least 2 threads (producer and consumer)",
        actual=f"{thread_count} threads found",
        check_type="constraint",
    ))

    # Check 9: Cross-platform contamination
    cross_plat = check_no_cross_platform_apis(generated_code, skip_platforms=["Linux_Userspace"])
    details.append(CheckDetail(
        check_name="no_cross_platform_apis",
        passed=len(cross_plat) == 0,
        expected="No FreeRTOS/Arduino/STM32_HAL APIs",
        actual="clean" if not cross_plat else f"found: {[a for a, _ in cross_plat]}",
        check_type="constraint",
    ))

    return details
