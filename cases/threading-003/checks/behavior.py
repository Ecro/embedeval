"""Behavioral checks for semaphore-based event signaling."""

import re

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate semaphore signaling behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: Semaphore initial count is 0 (consumer must block until producer signals)
    # (LLM failure: initial count 1 — consumer does not block, spurious first execution)
    sem_define_match = re.search(
        r"K_SEM_DEFINE\s*\(\s*\w+\s*,\s*(\d+)\s*,\s*(\d+)\s*\)",
        generated_code,
    )
    initial_count_zero = False
    if sem_define_match:
        initial_count_zero = int(sem_define_match.group(1)) == 0
    details.append(
        CheckDetail(
            check_name="semaphore_initial_count_zero",
            passed=initial_count_zero,
            expected="K_SEM_DEFINE initial count = 0 (consumer blocks until signaled)",
            actual=f"initial={sem_define_match.group(1)}" if sem_define_match else "K_SEM_DEFINE not found",
            check_type="constraint",
        )
    )

    # Check 2: Semaphore maximum count is 1 (binary semaphore for event signaling)
    # (LLM failure: max count > 1 allows stacking signals, losing binary property)
    max_count_one = False
    if sem_define_match:
        max_count_one = int(sem_define_match.group(2)) == 1
    details.append(
        CheckDetail(
            check_name="semaphore_max_count_one",
            passed=max_count_one,
            expected="K_SEM_DEFINE max count = 1 (binary semaphore)",
            actual=f"max={sem_define_match.group(2)}" if sem_define_match else "K_SEM_DEFINE not found",
            check_type="constraint",
        )
    )

    # Check 3: Consumer uses K_FOREVER (blocking wait, not polling)
    # (LLM failure: using K_NO_WAIT — busy-polls instead of blocking)
    consumer_blocks = (
        "K_FOREVER" in generated_code
        and "k_sem_take" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="consumer_uses_k_forever",
            passed=consumer_blocks,
            expected="k_sem_take uses K_FOREVER (blocking wait)",
            actual="present" if consumer_blocks else "K_NO_WAIT or timeout used",
            check_type="constraint",
        )
    )

    # Check 4: Producer sleeps before giving semaphore (simulates event production delay)
    # (LLM failure: give called in tight loop with no sleep)
    give_pos = generated_code.find("k_sem_give")
    producer_sleeps = False
    if give_pos >= 0:
        # Look for k_sleep within 400 chars before give
        nearby = generated_code[max(0, give_pos - 400):give_pos]
        producer_sleeps = "k_sleep" in nearby or "k_msleep" in nearby
    details.append(
        CheckDetail(
            check_name="producer_sleeps_before_signal",
            passed=producer_sleeps,
            expected="Producer calls k_sleep before k_sem_give",
            actual="present" if producer_sleeps else "missing",
            check_type="constraint",
        )
    )

    # Check 5: Both give and take are present (not just one direction)
    has_both = "k_sem_give" in generated_code and "k_sem_take" in generated_code
    details.append(
        CheckDetail(
            check_name="both_give_and_take_present",
            passed=has_both,
            expected="Both k_sem_give and k_sem_take present",
            actual=f"give={'present' if 'k_sem_give' in generated_code else 'missing'}, "
                   f"take={'present' if 'k_sem_take' in generated_code else 'missing'}",
            check_type="exact_match",
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
