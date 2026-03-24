"""Behavioral checks for lock-free SPSC ring queue."""

import re

from embedeval.check_utils import (
    check_no_cross_platform_apis,
    check_no_isr_forbidden,
    strip_comments,
)
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate SPSC queue behavioral correctness."""
    details: list[CheckDetail] = []

    stripped = strip_comments(generated_code)

    # Check 1: spsc_queue struct (or equivalent) defined
    has_struct = bool(
        re.search(r"struct\s+\w*(?:spsc|queue|ring|fifo)\w*\s*\{", generated_code, re.IGNORECASE)
    )
    details.append(
        CheckDetail(
            check_name="queue_struct_defined",
            passed=has_struct,
            expected="SPSC queue struct defined",
            actual="struct found" if has_struct else "no queue struct",
            check_type="exact_match",
        )
    )

    # Check 2: Push (producer) function defined
    has_push = bool(
        re.search(r"\b\w*(?:push|put|enq|write|produce)\w*\s*\(", generated_code, re.IGNORECASE)
    )
    details.append(
        CheckDetail(
            check_name="push_function_defined",
            passed=has_push,
            expected="Producer push/put function defined",
            actual="push function found" if has_push else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: Pop (consumer) function defined
    has_pop = bool(
        re.search(r"\b\w*(?:pop|get|deq|read|consume)\w*\s*\(", generated_code, re.IGNORECASE)
    )
    details.append(
        CheckDetail(
            check_name="pop_function_defined",
            passed=has_pop,
            expected="Consumer pop/get function defined",
            actual="pop function found" if has_pop else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Full condition checked (prevent overflow)
    # LLM failure: no full check — producer overwrites unconsumed data
    has_full_check = bool(
        re.search(
            r"(return\s+-\d+|full|== \w*SIZE|== \w*DEPTH)",
            generated_code,
            re.IGNORECASE,
        )
    )
    details.append(
        CheckDetail(
            check_name="full_condition_checked",
            passed=has_full_check,
            expected="Full condition checked in push (overflow guard)",
            actual="full check found" if has_full_check else "no overflow guard",
            check_type="constraint",
        )
    )

    # Check 5: Empty condition checked (prevent underflow)
    has_empty_check = bool(
        re.search(
            r"(return\s+-\d+|empty|== \w*SIZE|read.*==.*write|write.*==.*read)",
            generated_code,
            re.IGNORECASE,
        )
    )
    details.append(
        CheckDetail(
            check_name="empty_condition_checked",
            passed=has_empty_check,
            expected="Empty condition checked in pop (underflow guard)",
            actual="empty check found" if has_empty_check else "no underflow guard",
            check_type="constraint",
        )
    )

    # Check 6: Memory barrier present (compiler_barrier, __dmb, atomic_thread_fence)
    barrier_patterns = ["compiler_barrier", "__dmb", "atomic_thread_fence", "__DSB", "__ISB",
                        "barrier()", "COMPILER_BARRIER"]
    has_barrier = any(b in generated_code for b in barrier_patterns)
    details.append(
        CheckDetail(
            check_name="memory_barrier_present",
            passed=has_barrier,
            expected="Memory barrier before advancing index (compiler_barrier or __dmb)",
            actual="barrier found" if has_barrier else "no memory barrier",
            check_type="constraint",
        )
    )

    # Check 7: No forbidden APIs inside ISR bodies (if ISR bodies present)
    # LLM failure: calling k_malloc or printk inside an ISR that pushes to the queue
    isr_violations = check_no_isr_forbidden(generated_code)
    details.append(
        CheckDetail(
            check_name="no_forbidden_apis_in_isr",
            passed=len(isr_violations) == 0,
            expected="No printk/k_malloc/k_sleep inside ISR bodies (if any)",
            actual="clean" if not isr_violations else f"violations: {isr_violations}",
            check_type="constraint",
        )
    )

    # Check 8: No cross-platform API contamination
    # LLM failure: using xQueueSend (FreeRTOS) or pthread_mutex (POSIX)
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
