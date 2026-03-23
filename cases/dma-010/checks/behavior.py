"""Behavioral checks for zero-copy DMA double buffer swap."""

import re

from embedeval.models import CheckDetail


def _strip_c_comments(code: str) -> str:
    """Remove C-style line comments to avoid false positives in comment text."""
    return re.sub(r"//[^\n]*", "", code)


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate DMA double buffer behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    code_no_comments = _strip_c_comments(generated_code)

    # Check 1: Two separate buffer arrays (not a 2D array indexed by [0][x] and [1][x])
    has_buf_a = "buf_a" in generated_code or "buffer_a" in generated_code or "ping" in generated_code
    has_buf_b = "buf_b" in generated_code or "buffer_b" in generated_code or "pong" in generated_code
    separate_bufs = has_buf_a and has_buf_b
    details.append(
        CheckDetail(
            check_name="two_separate_buffer_arrays",
            passed=separate_bufs,
            expected="Two distinct buffer arrays for ping-pong (not one 2D array)",
            actual="separate arrays" if separate_bufs else "one or both buffers missing",
            check_type="constraint",
        )
    )

    # Check 2: Atomic swap operation present
    has_atomic_swap = (
        "atomic_set" in generated_code
        or "atomic_cas" in generated_code
        or ("atomic" in generated_code and ("1 -" in generated_code or "^ 1" in generated_code))
    )
    details.append(
        CheckDetail(
            check_name="atomic_swap_present",
            passed=has_atomic_swap,
            expected="Atomic swap of buffer index (atomic_set or atomic_cas with 1 - current)",
            actual="present" if has_atomic_swap else "missing atomic swap — race condition possible",
            check_type="constraint",
        )
    )

    # Check 3: dma_reload called to switch buffers
    has_reload = "dma_reload" in generated_code
    details.append(
        CheckDetail(
            check_name="dma_reload_for_next_buffer",
            passed=has_reload,
            expected="dma_reload() called to point DMA at next buffer",
            actual="present" if has_reload else "missing — DMA not reloaded for double-buffering",
            check_type="constraint",
        )
    )

    # Check 4: No memcpy between buffers (zero-copy requirement)
    # Strip comments so "no memcpy" in a comment does not trigger false positive,
    # but also ignore mentions of memcpy in a comment explaining what NOT to do.
    has_memcpy = "memcpy(" in code_no_comments
    details.append(
        CheckDetail(
            check_name="no_memcpy_between_buffers",
            passed=not has_memcpy,
            expected="No memcpy() calls — zero-copy means CPU reads directly from DMA buffer",
            actual="clean" if not has_memcpy else "memcpy() call found — defeats zero-copy purpose",
            check_type="constraint",
        )
    )

    # Check 5: Semaphore used for CPU/DMA synchronization
    has_sem = "k_sem_take" in generated_code and "k_sem_give" in generated_code
    details.append(
        CheckDetail(
            check_name="semaphore_cpu_dma_sync",
            passed=has_sem,
            expected="Semaphore used to signal CPU when DMA buffer is ready",
            actual="present" if has_sem else "missing synchronization between DMA and CPU",
            check_type="constraint",
        )
    )

    # Check 6: Processing loop iterates (not just single shot)
    has_loop = "for" in generated_code or "while" in generated_code
    details.append(
        CheckDetail(
            check_name="processing_loop_present",
            passed=has_loop,
            expected="Loop present for repeated ping-pong buffer processing",
            actual="present" if has_loop else "missing loop — single shot only",
            check_type="constraint",
        )
    )

    return details
