"""Behavioral checks for ISR-safe ring buffer implementation."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate ring buffer behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: Ring buffer struct defined
    has_struct = "struct" in generated_code and (
        "ring_buf" in generated_code.lower()
        or "ringbuf" in generated_code.lower()
        or "ring_buffer" in generated_code.lower()
    )
    details.append(
        CheckDetail(
            check_name="ring_buffer_struct_defined",
            passed=has_struct,
            expected="Ring buffer struct definition",
            actual="struct found" if has_struct else "no ring buffer struct",
            check_type="exact_match",
        )
    )

    # Check 2: Init function present
    has_init = bool(
        re.search(r"\b\w*init\w*\s*\(", generated_code, re.IGNORECASE)
    )
    details.append(
        CheckDetail(
            check_name="init_function_present",
            passed=has_init,
            expected="Initialization function",
            actual="init function found" if has_init else "no init function",
            check_type="exact_match",
        )
    )

    # Check 3: Put/get (produce/consume) functions present
    has_put = bool(
        re.search(r"\b\w*(put|write|enqueue|produce|push)\w*\s*\(", generated_code, re.IGNORECASE)
    )
    has_get = bool(
        re.search(r"\b\w*(get|read|dequeue|consume|pop)\w*\s*\(", generated_code, re.IGNORECASE)
    )
    details.append(
        CheckDetail(
            check_name="put_get_functions_present",
            passed=has_put and has_get,
            expected="Both put/produce and get/consume functions",
            actual=f"put={has_put}, get={has_get}",
            check_type="exact_match",
        )
    )

    # Check 4: Buffer full handling
    has_full_check = bool(
        re.search(r"(full|== \(uint32_t\)|next_head ==|return -1.*full)", generated_code, re.IGNORECASE)
        or "is_full" in generated_code.lower()
        or ("return -1" in generated_code and "full" in generated_code.lower())
    )
    details.append(
        CheckDetail(
            check_name="buffer_full_handling",
            passed=has_full_check,
            expected="Buffer full condition handling",
            actual="full handling found" if has_full_check else "no full handling",
            check_type="constraint",
        )
    )

    # Check 5: Buffer empty handling
    has_empty_check = bool(
        re.search(r"(empty|head == tail|tail == head|return -1.*empty)", generated_code, re.IGNORECASE)
        or "is_empty" in generated_code.lower()
        or ("return -1" in generated_code and "empty" in generated_code.lower())
    )
    details.append(
        CheckDetail(
            check_name="buffer_empty_handling",
            passed=has_empty_check,
            expected="Buffer empty condition handling",
            actual="empty handling found" if has_empty_check else "no empty handling",
            check_type="constraint",
        )
    )

    # Check 6: FIFO ordering maintained (uses head/tail or read/write indices)
    has_fifo = bool(
        re.search(r"(head|tail|read_idx|write_idx|rd_idx|wr_idx)", generated_code, re.IGNORECASE)
    )
    details.append(
        CheckDetail(
            check_name="fifo_ordering",
            passed=has_fifo,
            expected="FIFO ordering via head/tail indices",
            actual="head/tail indices found" if has_fifo else "no FIFO structure",
            check_type="constraint",
        )
    )

    # Check 7: Atomic operations used for indices
    atomic_patterns = ["atomic_t", "atomic_set", "atomic_get", "atomic_cas"]
    has_atomic_indices = any(p in generated_code for p in atomic_patterns)
    details.append(
        CheckDetail(
            check_name="atomic_index_operations",
            passed=has_atomic_indices,
            expected="Atomic operations for index management",
            actual="atomic operations found" if has_atomic_indices else "no atomic ops",
            check_type="exact_match",
        )
    )

    # Check 8: No mutex/semaphore usage (lock-free constraint)
    mutex_patterns = ["k_mutex", "k_sem", "pthread_mutex", "k_spin_lock"]
    has_mutex = any(p in generated_code for p in mutex_patterns)
    details.append(
        CheckDetail(
            check_name="no_mutex_semaphore",
            passed=not has_mutex,
            expected="No mutex/semaphore usage (lock-free)",
            actual="mutex/semaphore found" if has_mutex else "lock-free confirmed",
            check_type="constraint",
        )
    )

    return details
