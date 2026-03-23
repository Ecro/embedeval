"""Behavioral checks for custom work queue with delayed submission."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate work queue behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: Stack size is at least 2048
    # (LLM failure: using 512 or 1024 — work queue needs larger stack for its own context)
    stack_match = re.search(
        r"K_THREAD_STACK_DEFINE\s*\(\s*\w+\s*,\s*(\d+)\s*\)",
        generated_code,
    )
    stack_size_ok = False
    stack_size_val = 0
    if stack_match:
        stack_size_val = int(stack_match.group(1))
        stack_size_ok = stack_size_val >= 2048
    details.append(
        CheckDetail(
            check_name="stack_size_adequate",
            passed=stack_size_ok,
            expected="Work queue stack size >= 2048",
            actual=f"size={stack_size_val}" if stack_match else "K_THREAD_STACK_DEFINE not found",
            check_type="constraint",
        )
    )

    # Check 2: Work handler does NOT call k_sleep (handlers must not block)
    # (LLM failure: blocking inside work handler stalls the entire work queue)
    handler_has_sleep = False
    handler_match = re.search(
        r"(static\s+)?void\s+\w+\s*\(\s*struct\s+k_work\s*\*\s*\w*\s*\)"
        r"\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}",
        generated_code,
        re.DOTALL,
    )
    if handler_match:
        handler_body = handler_match.group(2)
        handler_has_sleep = "k_sleep" in handler_body or "k_msleep" in handler_body
    details.append(
        CheckDetail(
            check_name="work_handler_does_not_block",
            passed=not handler_has_sleep,
            expected="Work handler does NOT call k_sleep (must not block)",
            actual="non-blocking" if not handler_has_sleep else "handler blocks with k_sleep",
            check_type="constraint",
        )
    )

    # Check 3: k_work_init_delayable called before scheduling
    # (LLM failure: scheduling uninitialized work item)
    has_init_delayable = "k_work_init_delayable" in generated_code
    details.append(
        CheckDetail(
            check_name="delayable_work_initialized",
            passed=has_init_delayable,
            expected="k_work_init_delayable() called to initialize work item",
            actual="present" if has_init_delayable else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: k_work_schedule_for_queue used (not k_work_schedule for system queue)
    # (LLM failure: submitting to default system queue, not the custom queue)
    has_schedule_for_queue = "k_work_schedule_for_queue" in generated_code
    uses_system_queue_only = (
        "k_work_schedule(" in generated_code
        and not has_schedule_for_queue
    )
    details.append(
        CheckDetail(
            check_name="submits_to_custom_queue",
            passed=has_schedule_for_queue and not uses_system_queue_only,
            expected="k_work_schedule_for_queue() used to target custom queue",
            actual="custom queue" if has_schedule_for_queue else "system queue or missing",
            check_type="constraint",
        )
    )

    # Check 5: K_THREAD_STACK_SIZEOF used in k_work_queue_start (not raw integer)
    # (LLM failure: passing raw stack size number instead of macro)
    has_stack_sizeof = "K_THREAD_STACK_SIZEOF" in generated_code
    details.append(
        CheckDetail(
            check_name="stack_sizeof_macro_used",
            passed=has_stack_sizeof,
            expected="K_THREAD_STACK_SIZEOF() passed to k_work_queue_start",
            actual="present" if has_stack_sizeof else "missing (raw integer used)",
            check_type="constraint",
        )
    )

    return details
