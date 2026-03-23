"""Behavioral checks for double-buffer (ping-pong) pattern."""

import re

from embedeval.models import CheckDetail


def _extract_function_body(code: str, func_name: str) -> str:
    """Extract the body of a C function by matching braces, not regex."""
    pattern = re.compile(
        r'\b' + re.escape(func_name) + r'\s*\([^)]*\)\s*\{',
        re.DOTALL
    )
    m = pattern.search(code)
    if not m:
        return ""
    start = m.end() - 1  # position of opening '{'
    depth = 0
    for i, ch in enumerate(code[start:], start):
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return code[start + 1:i]
    return ""


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate double-buffer behavioral properties."""
    details: list[CheckDetail] = []

    # Find ISR function name heuristically
    isr_name_match = re.search(r'\b(isr_handler|irq_handler|sensor_isr|timer_isr)\b', generated_code)
    isr_name = isr_name_match.group(1) if isr_name_match else "isr_handler"
    isr_body = _extract_function_body(generated_code, isr_name)

    # Check 1: ISR fills buffer THEN atomically swaps index
    # With proper body extraction, we check order of assignment and atomic_set
    fill_pos = isr_body.find("buf[") if isr_body else -1
    if fill_pos == -1 and isr_body:
        # Some implementations use a different buffer name
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
    # Matches: "1 - idx", "1 - (int)atomic_get(...)", "idx ^ 1", "!idx"
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

    # Check 5: k_sleep present (scheduling)
    has_sleep = "k_sleep" in generated_code
    details.append(
        CheckDetail(
            check_name="k_sleep_present",
            passed=has_sleep,
            expected="k_sleep() present for scheduling",
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

    return details
