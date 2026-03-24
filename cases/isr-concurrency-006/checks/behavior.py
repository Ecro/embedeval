"""Behavioral checks for ISR-safe FIFO with k_fifo."""

import re

from embedeval.check_utils import (
    check_no_cross_platform_apis,
    check_no_isr_forbidden,
    find_isr_bodies,
    strip_comments,
)
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate k_fifo behavioral correctness for ISR-to-thread transfer."""
    details: list[CheckDetail] = []

    stripped = strip_comments(generated_code)

    # Check 1: Static allocation — no k_malloc anywhere
    # LLM failure: calling k_malloc in ISR handler to allocate item
    has_kmalloc = "k_malloc" in stripped
    details.append(
        CheckDetail(
            check_name="static_allocation_only",
            passed=not has_kmalloc,
            expected="Items statically allocated (no k_malloc)",
            actual="uses k_malloc" if has_kmalloc else "static alloc confirmed",
            check_type="constraint",
        )
    )

    # Check 2: k_fifo_get NOT inside ISR handler body using find_isr_bodies
    # LLM failure: calling blocking k_fifo_get inside the ISR
    isr_bodies = find_isr_bodies(stripped)
    isr_has_get = any("k_fifo_get" in body for body in isr_bodies)
    details.append(
        CheckDetail(
            check_name="k_fifo_get_not_in_isr",
            passed=not isr_has_get,
            expected="k_fifo_get() NOT called inside ISR (it blocks)",
            actual="ISR calls k_fifo_get (BUG)" if isr_has_get else "k_fifo_get in thread only",
            check_type="constraint",
        )
    )

    # Check 3: Consumer thread uses k_fifo_get with timeout (not K_NO_WAIT in a tight loop)
    has_get_with_timeout = bool(
        re.search(r"k_fifo_get\s*\([^,]+,\s*K_(FOREVER|MSEC|SECONDS|TICKS)\b", generated_code)
    )
    details.append(
        CheckDetail(
            check_name="consumer_uses_blocking_get",
            passed=has_get_with_timeout,
            expected="k_fifo_get() with blocking timeout (K_FOREVER or K_MSEC)",
            actual="blocking get found" if has_get_with_timeout else "no blocking get (may spin)",
            check_type="constraint",
        )
    )

    # Check 4: Static item pool defined (array of structs)
    # LLM failure: declaring a single item variable instead of a pool
    has_pool = bool(
        re.search(r"static\s+(?:struct\s+)?\w+\s+\w+\s*\[\s*\w+\s*\]", generated_code)
    )
    details.append(
        CheckDetail(
            check_name="static_item_pool",
            passed=has_pool,
            expected="Static array pool for k_fifo items",
            actual="pool found" if has_pool else "no static array pool",
            check_type="exact_match",
        )
    )

    # Check 5: Consumer thread defined (separate function from main)
    thread_fns = re.findall(
        r"void\s+(\w+)\s*\(\s*(?:void\s*\*[^,)]*(?:,\s*void\s*\*[^,)]*){0,2})?\s*\)",
        generated_code,
    )
    consumer_names = [
        n for n in thread_fns
        if any(kw in n.lower() for kw in ["thread", "consumer", "recv", "process", "task"])
    ]
    has_consumer_thread = len(consumer_names) > 0 or (
        "K_THREAD_DEFINE" in generated_code or "k_thread_create" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="consumer_thread_defined",
            passed=has_consumer_thread,
            expected="Consumer thread defined (separate from main/ISR)",
            actual="consumer thread found" if has_consumer_thread else "no consumer thread",
            check_type="exact_match",
        )
    )

    # Check 6: No forbidden APIs inside ISR bodies (strengthened with check_utils)
    # LLM failure: calling printk inside the ISR fifo put handler
    isr_violations = check_no_isr_forbidden(generated_code)
    details.append(
        CheckDetail(
            check_name="no_forbidden_apis_in_isr",
            passed=len(isr_violations) == 0,
            expected="No printk/k_malloc/k_sleep inside ISR bodies",
            actual="clean" if not isr_violations else f"violations: {isr_violations}",
            check_type="constraint",
        )
    )

    # Check 7: No cross-platform API contamination
    # LLM failure: using xQueueSendFromISR (FreeRTOS) instead of k_fifo_put
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
