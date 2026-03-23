"""Behavioral checks for lock-free SPSC ring queue."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate SPSC queue behavioral correctness."""
    details: list[CheckDetail] = []

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

    return details
