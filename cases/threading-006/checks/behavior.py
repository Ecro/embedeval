"""Behavioral checks for deadlock-free multi-mutex acquisition."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate lock ordering to prevent deadlock."""
    details: list[CheckDetail] = []

    # Check 1: Lock order A-before-B in both thread functions
    # LLM failure: thread_two locks B first (creating circular wait with thread_one)
    # Find positions of mutex_a and mutex_b lock calls
    lock_a_positions = [m.start() for m in re.finditer(r"k_mutex_lock\s*\(\s*&?\s*mutex_a\b", generated_code)]
    lock_b_positions = [m.start() for m in re.finditer(r"k_mutex_lock\s*\(\s*&?\s*mutex_b\b", generated_code)]

    # For each lock_a, the nearest subsequent lock_b should come after it
    lock_order_correct = True
    if lock_a_positions and lock_b_positions:
        for pos_a in lock_a_positions:
            # Check if there's a lock_b that comes after this lock_a
            # and before the next lock_a
            next_a = min((p for p in lock_a_positions if p > pos_a), default=len(generated_code))
            b_after_a = any(pos_a < p < next_a for p in lock_b_positions)
            if not b_after_a:
                lock_order_correct = False
                break
    else:
        # Could not determine — look for generic mutex names
        lock_order_correct = len(lock_a_positions) >= 2 or len(lock_b_positions) >= 2

    details.append(
        CheckDetail(
            check_name="lock_order_a_before_b",
            passed=lock_order_correct,
            expected="mutex_a locked BEFORE mutex_b in both threads",
            actual="consistent A-B ordering" if lock_order_correct else "inconsistent ordering (deadlock risk)",
            check_type="constraint",
        )
    )

    # Check 2: Unlock order B-before-A (reverse of lock order)
    unlock_a_positions = [m.start() for m in re.finditer(r"k_mutex_unlock\s*\(\s*&?\s*mutex_a\b", generated_code)]
    unlock_b_positions = [m.start() for m in re.finditer(r"k_mutex_unlock\s*\(\s*&?\s*mutex_b\b", generated_code)]

    # Each unlock_b should come before the nearest unlock_a after it
    unlock_order_correct = True
    if unlock_b_positions and unlock_a_positions:
        for pos_b in unlock_b_positions:
            next_b = min((p for p in unlock_b_positions if p > pos_b), default=len(generated_code))
            a_after_b = any(pos_b < p < next_b for p in unlock_a_positions)
            if not a_after_b:
                unlock_order_correct = False
                break
    else:
        unlock_order_correct = len(unlock_a_positions) >= 1 or len(unlock_b_positions) >= 1

    details.append(
        CheckDetail(
            check_name="unlock_order_b_before_a",
            passed=unlock_order_correct,
            expected="mutex_b unlocked BEFORE mutex_a (reverse of lock order)",
            actual="reverse unlock order confirmed" if unlock_order_correct else "wrong unlock order",
            check_type="constraint",
        )
    )

    # Check 3: Both threads defined
    thread_fns = re.findall(
        r"void\s+(\w*(?:thread|task)\w*)\s*\(",
        generated_code,
        re.IGNORECASE,
    )
    has_two_threads = len(thread_fns) >= 2
    details.append(
        CheckDetail(
            check_name="two_thread_functions",
            passed=has_two_threads,
            expected="At least two thread functions defined",
            actual=f"thread functions={thread_fns}",
            check_type="exact_match",
        )
    )

    # Check 4: K_FOREVER used as lock timeout (not K_NO_WAIT which could starve)
    has_forever = "K_FOREVER" in generated_code
    details.append(
        CheckDetail(
            check_name="lock_with_k_forever",
            passed=has_forever,
            expected="K_FOREVER used as mutex timeout",
            actual="present" if has_forever else "missing",
            check_type="constraint",
        )
    )

    # Check 5: Threads loop (work is repeated)
    has_loop = bool(re.search(r"while\s*\(\s*(?:1|true)\s*\)", generated_code))
    details.append(
        CheckDetail(
            check_name="threads_loop",
            passed=has_loop,
            expected="Threads repeat in a loop",
            actual="loop found" if has_loop else "no loop (single shot?)",
            check_type="constraint",
        )
    )

    return details
