"""Behavioral checks for ISR-safe FIFO with k_fifo."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate k_fifo behavioral correctness for ISR-to-thread transfer."""
    details: list[CheckDetail] = []

    # Check 1: Static allocation — no k_malloc anywhere
    # LLM failure: calling k_malloc in ISR handler to allocate item
    # Strip comments before checking to avoid false positives
    import re as _re
    stripped = _re.sub(r"/\*.*?\*/", "", generated_code, flags=_re.DOTALL)
    stripped = _re.sub(r"//.*", "", stripped)
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

    # Check 2: k_fifo_get NOT inside ISR handler body
    # LLM failure: calling blocking k_fifo_get inside the ISR
    # Heuristic: look for ISR-like function (void *_isr, irq_handler, ISR_DIRECT) containing k_fifo_get
    isr_pattern = re.search(
        r"(void\s+\w*(?:isr|irq|handler|interrupt)\w*\s*\([^)]*\)\s*\{)(.*?)(\n\})",
        generated_code,
        re.IGNORECASE | re.DOTALL,
    )
    isr_has_get = False
    if isr_pattern:
        isr_body = isr_pattern.group(2)
        isr_has_get = "k_fifo_get" in isr_body
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
    # K_FOREVER or K_MSEC timeout preferred; K_NO_WAIT in a loop wastes CPU
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
    # Filter out ISR-like names; look for thread-like names
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

    return details
