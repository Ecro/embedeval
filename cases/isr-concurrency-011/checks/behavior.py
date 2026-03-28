"""Behavioral checks for ISR stack overflow protection."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate stack protection in ISR-driven data collection."""
    details: list[CheckDetail] = []

    # Check 1: Stack size explicitly defined (not default)
    has_stack_define = bool(re.search(
        r'K_THREAD_STACK_DEFINE\s*\(', generated_code,
    )) or bool(re.search(
        r'#define\s+\w*(?:STACK|stack)\w*\s+\d+', generated_code,
    )) or bool(re.search(
        r'K_THREAD_DEFINE\s*\([^,]+,\s*(?:\d+|[A-Z_]+)',
        generated_code,
    ))
    details.append(
        CheckDetail(
            check_name="stack_size_explicitly_defined",
            passed=has_stack_define,
            expected="Thread stack size explicitly defined (not relying on default)",
            actual="present" if has_stack_define
            else "MISSING (stack size not explicitly set)",
            check_type="constraint",
        )
    )

    # Check 2: CONFIG_STACK_SENTINEL or stack canary protection mentioned/configured
    has_stack_protection = any(s in generated_code for s in [
        "CONFIG_STACK_SENTINEL",
        "CONFIG_STACK_CANARIES",
        "CONFIG_HW_STACK_PROTECTION",
        "CONFIG_MPU_STACK_GUARD",
        "K_THREAD_STACK_SIZEOF",
        "k_thread_stack_space_get",
        "CONFIG_THREAD_STACK_INFO",
    ])
    details.append(
        CheckDetail(
            check_name="stack_overflow_protection_configured",
            passed=has_stack_protection,
            expected="Stack overflow protection configured (SENTINEL, canary, or MPU guard)",
            actual="present" if has_stack_protection
            else "MISSING (no stack overflow detection mechanism)",
            check_type="constraint",
        )
    )

    # Check 3: ISR uses semaphore (not mutex) for signaling
    # Extract ISR function body and verify k_sem_give is inside it
    isr_body_match = re.search(
        r'(?:callback|isr|handler|irq)\s*\([^)]*\)\s*\{'
        r'([^{}]*(?:\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}[^{}]*)*)\}',
        generated_code, re.DOTALL | re.IGNORECASE,
    )
    has_sem_give_in_callback = (
        bool(isr_body_match)
        and "k_sem_give" in isr_body_match.group(1)
    )
    details.append(
        CheckDetail(
            check_name="isr_signals_via_semaphore",
            passed=has_sem_give_in_callback,
            expected="ISR/callback uses k_sem_give (not mutex) to signal thread",
            actual="present" if has_sem_give_in_callback
            else "MISSING (ISR should use k_sem_give for thread signaling)",
            check_type="constraint",
        )
    )

    # Check 4: No forbidden APIs in ISR (no malloc, no mutex lock, no sleep)
    # Reuse isr_body_match from check 3 (supports two nesting levels)
    callback_body = isr_body_match
    forbidden_in_isr = ["k_mutex_lock", "k_sleep", "k_msleep", "malloc(", "printk("]
    has_forbidden = False
    if callback_body:
        body = callback_body.group(1)
        has_forbidden = any(f in body for f in forbidden_in_isr)

    details.append(
        CheckDetail(
            check_name="no_forbidden_apis_in_isr",
            passed=not has_forbidden,
            expected="No blocking/allocating calls in ISR body",
            actual="clean" if not has_forbidden
            else "FORBIDDEN API in ISR (mutex/sleep/malloc/printk)",
            check_type="constraint",
        )
    )

    # Check 5: Ring buffer or bounded buffer for ISR data
    has_ring_buf = any(s in generated_code for s in [
        "ring_buf", "RING_BUF", "head", "tail",
        "write_idx", "read_idx", "wr_idx", "rd_idx",
    ])
    details.append(
        CheckDetail(
            check_name="bounded_buffer_for_isr_data",
            passed=has_ring_buf,
            expected="Ring buffer or bounded buffer for ISR data collection",
            actual="present" if has_ring_buf
            else "MISSING (ISR data needs bounded buffer)",
            check_type="constraint",
        )
    )

    return details
