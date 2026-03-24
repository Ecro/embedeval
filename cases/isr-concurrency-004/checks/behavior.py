"""Behavioral checks for double-buffer (ping-pong) pattern."""

import re

from embedeval.check_utils import (
    check_no_cross_platform_apis,
    check_no_isr_forbidden,
    extract_function_body,
    strip_comments,
)
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate double-buffer behavioral properties."""
    details: list[CheckDetail] = []

    stripped = strip_comments(generated_code)

    # Find ISR function name heuristically
    isr_name_match = re.search(r'\b(isr_handler|irq_handler|sensor_isr|timer_isr)\b', generated_code)
    isr_name = isr_name_match.group(1) if isr_name_match else "isr_handler"
    isr_body = extract_function_body(generated_code, isr_name) or ""

    # Check 1: ISR fills buffer THEN atomically swaps index
    fill_pos = isr_body.find("buf[") if isr_body else -1
    if fill_pos == -1 and isr_body:
        fill_pos = isr_body.find("[i]") if "[i]" in isr_body else isr_body.find("=")
    swap_pos = isr_body.find("atomic_set") if isr_body else -1
    fill_before_swap = fill_pos != -1 and swap_pos != -1 and fill_pos < swap_pos
    details.append(
        CheckDetail(
            check_name="fill_before_atomic_swap",
            passed=fill_before_swap,
            expected="ISR fills buffer THEN atomically swaps index",
            actual="correct order" if fill_before_swap else "wrong order or not found",
            check_type="constraint",
        )
    )

    # Check 2: Thread reads OPPOSITE buffer from ISR (1 - write_idx or equivalent)
    has_opposite = bool(re.search(
        r'1\s*-\s*(?:\(int\)\s*)?(?:atomic_get\s*\(|write_idx\b|\w+_idx\b)|'
        r'\w+_idx\s*\^\s*1|'
        r'!\s*\w+_idx\b',
        generated_code
    ))
    details.append(
        CheckDetail(
            check_name="thread_reads_opposite_buffer",
            passed=has_opposite,
            expected="Thread reads buffer at index (1 - write_idx)",
            actual="present" if has_opposite else "missing (may read same buffer as ISR!)",
            check_type="constraint",
        )
    )

    # Check 3: Processor thread defined
    has_thread = (
        "K_THREAD_DEFINE" in generated_code
        or "k_thread_create" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="processor_thread_defined",
            passed=has_thread,
            expected="Processor thread defined",
            actual="present" if has_thread else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Buffer data aggregated (sum or similar processing in thread)
    has_aggregation = bool(re.search(
        r'\bsum\b|\baccum\b|\btotal\b|\bresult\b', generated_code, re.IGNORECASE
    ))
    details.append(
        CheckDetail(
            check_name="buffer_data_aggregated",
            passed=has_aggregation,
            expected="Thread aggregates buffer data (sum/accumulate)",
            actual="present" if has_aggregation else "missing",
            check_type="constraint",
        )
    )

    # Check 5: k_sleep/k_msleep/k_usleep present (scheduling)
    has_sleep = bool(re.search(r'\bk_(?:m?sleep|usleep)\b', generated_code))
    details.append(
        CheckDetail(
            check_name="k_sleep_present",
            passed=has_sleep,
            expected="k_sleep/k_msleep/k_usleep present for scheduling",
            actual="present" if has_sleep else "missing",
            check_type="constraint",
        )
    )

    # Check 6: Printed output present
    has_print = "printk" in generated_code or "printf" in generated_code
    details.append(
        CheckDetail(
            check_name="output_printed",
            passed=has_print,
            expected="Processed result printed",
            actual="present" if has_print else "missing",
            check_type="constraint",
        )
    )

    # Check 7: No forbidden APIs inside ISR bodies
    # LLM failure: putting printk or k_malloc in the ISR swap body
    isr_violations = check_no_isr_forbidden(generated_code)
    details.append(
        CheckDetail(
            check_name="no_forbidden_apis_in_isr",
            passed=len(isr_violations) == 0,
            expected="No printk/k_malloc/k_sleep inside ISR bodies",
            actual="clean" if not isr_violations else f"violations: {isr_violations}",
            check_type="constraint",
        )
    )

    # Check 8: No cross-platform API contamination
    cross_platform = check_no_cross_platform_apis(generated_code, skip_platforms=["Linux_Userspace"])
    details.append(
        CheckDetail(
            check_name="no_cross_platform_apis",
            passed=len(cross_platform) == 0,
            expected="No FreeRTOS/Arduino/STM32_HAL/POSIX APIs",
            actual="clean" if not cross_platform else f"found: {[a for a, _ in cross_platform]}",
            check_type="constraint",
        )
    )

    return details
