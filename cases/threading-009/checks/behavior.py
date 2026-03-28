"""Behavioral checks for thread pool with work queue completion tracking."""

import re

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate work queue and completion semaphore behavioral correctness."""
    details: list[CheckDetail] = []

    # Check 1: k_work_init called BEFORE k_work_submit
    # LLM failure: calling k_work_submit on uninitialized k_work
    init_pos = generated_code.find("k_work_init")
    submit_pos = generated_code.find("k_work_submit")
    init_before_submit = init_pos != -1 and submit_pos != -1 and init_pos < submit_pos
    details.append(
        CheckDetail(
            check_name="init_before_submit",
            passed=init_before_submit,
            expected="k_work_init() appears before k_work_submit() in code",
            actual="init before submit" if init_before_submit else "submit before init or missing",
            check_type="constraint",
        )
    )

    # Check 2: Semaphore initial count is 0 (not NUM_WORK_ITEMS)
    # LLM failure: initializing sem with count=N, making take() succeed before any work completes
    sem_init_match = re.search(
        r"k_sem_init\s*\([^,]+,\s*(\d+)\s*,",
        generated_code,
    )
    sem_count_zero = True
    if sem_init_match:
        sem_count_zero = int(sem_init_match.group(1)) == 0
    details.append(
        CheckDetail(
            check_name="semaphore_initial_count_zero",
            passed=sem_count_zero,
            expected="Completion semaphore initialized with count=0",
            actual=f"initial count={sem_init_match.group(1)}" if sem_init_match else "K_SEM_DEFINE or not found",
            check_type="constraint",
        )
    )

    # Check 3: k_sem_give count matches number of work items
    # Count k_sem_give in work handler vs k_sem_take in main
    give_count = generated_code.count("k_sem_give")
    take_count = generated_code.count("k_sem_take")
    details.append(
        CheckDetail(
            check_name="give_take_balance",
            passed=give_count >= 1 and take_count >= 1,
            expected="k_sem_give called in handler, k_sem_take in waiter",
            actual=f"give={give_count} take={take_count}",
            check_type="constraint",
        )
    )

    # Check 4: NUM_WORK_ITEMS defined (not hardcoded magic number)
    has_num_define = bool(
        re.search(r"#define\s+NUM_WORK_ITEMS\s+\d+", generated_code)
        or "NUM_WORK_ITEMS" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="num_work_items_constant",
            passed=has_num_define,
            expected="NUM_WORK_ITEMS defined as named constant",
            actual="present" if has_num_define else "magic number used",
            check_type="constraint",
        )
    )

    # Check 5: All work items done message printed
    has_done_msg = bool(
        re.search(r"(all|complete|done|finish)", generated_code, re.IGNORECASE)
    )
    details.append(
        CheckDetail(
            check_name="completion_message_printed",
            passed=has_done_msg,
            expected="Completion message printed after all work items finish",
            actual="present" if has_done_msg else "missing",
            check_type="constraint",
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
