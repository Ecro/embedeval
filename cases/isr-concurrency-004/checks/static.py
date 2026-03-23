"""Static analysis checks for double-buffer (ping-pong) pattern."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate double-buffer ISR safety constraints."""
    details: list[CheckDetail] = []

    # Check 1: atomic_t used for buffer index tracking
    has_atomic_t = "atomic_t" in generated_code
    details.append(
        CheckDetail(
            check_name="atomic_t_for_index",
            passed=has_atomic_t,
            expected="atomic_t used for write_idx (buffer index)",
            actual="present" if has_atomic_t else "missing (non-atomic swap races!)",
            check_type="exact_match",
        )
    )

    # Check 2: atomic_set used to swap buffer index
    has_atomic_set = "atomic_set" in generated_code
    details.append(
        CheckDetail(
            check_name="atomic_set_for_swap",
            passed=has_atomic_set,
            expected="atomic_set() used to swap buffer index",
            actual="present" if has_atomic_set else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: atomic_get used to read buffer index
    has_atomic_get = "atomic_get" in generated_code
    details.append(
        CheckDetail(
            check_name="atomic_get_for_read",
            passed=has_atomic_get,
            expected="atomic_get() used to read buffer index",
            actual="present" if has_atomic_get else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Two buffers declared (array of 2 or two separate arrays)
    has_two_bufs = bool(
        re.search(r'\w+\s*\[\s*2\s*\]\s*\[', generated_code)
        or re.search(r'\w+_a\b.*\w+_b\b', generated_code, re.DOTALL)
        or generated_code.count("BUF_SIZE") >= 2
        or re.search(r'buf\s*\[2\]', generated_code)
    )
    details.append(
        CheckDetail(
            check_name="two_buffers_declared",
            passed=has_two_bufs,
            expected="Two buffers declared (e.g. buf[2][N] or buf_a/buf_b)",
            actual="present" if has_two_bufs else "missing (single buffer cannot ping-pong)",
            check_type="constraint",
        )
    )

    # Check 5: zephyr/sys/atomic.h included
    has_atomic_h = "zephyr/sys/atomic.h" in generated_code or "zephyr/kernel.h" in generated_code
    details.append(
        CheckDetail(
            check_name="atomic_header_included",
            passed=has_atomic_h,
            expected="zephyr/sys/atomic.h or zephyr/kernel.h included",
            actual="present" if has_atomic_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: No mutex or spinlock (wrong primitive for this pattern)
    has_locking = "k_mutex" in generated_code or "k_spinlock" in generated_code
    details.append(
        CheckDetail(
            check_name="no_locking_primitives",
            passed=not has_locking,
            expected="No k_mutex/k_spinlock (atomic swap should be sufficient)",
            actual="locking found (over-engineered)" if has_locking else "clean",
            check_type="constraint",
        )
    )

    return details
