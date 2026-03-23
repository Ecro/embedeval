"""Static analysis checks for ISR-to-thread k_msgq communication."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate k_msgq ISR safety constraints."""
    details: list[CheckDetail] = []

    # Check 1: k_msgq used (not a custom queue)
    has_msgq = "k_msgq" in generated_code
    details.append(
        CheckDetail(
            check_name="k_msgq_used",
            passed=has_msgq,
            expected="k_msgq API used",
            actual="present" if has_msgq else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: K_NO_WAIT used in ISR put (LLM failure: uses K_FOREVER which blocks)
    has_no_wait = "K_NO_WAIT" in generated_code
    details.append(
        CheckDetail(
            check_name="k_no_wait_in_isr_put",
            passed=has_no_wait,
            expected="K_NO_WAIT used in k_msgq_put (ISR must not block)",
            actual="present" if has_no_wait else "missing (may use K_FOREVER in ISR!)",
            check_type="constraint",
        )
    )

    # Check 3: K_FOREVER NOT used in k_msgq_put (blocking in ISR is fatal)
    # Allow K_FOREVER in k_msgq_get (consumer thread) but not in put
    # Search for k_msgq_put with K_FOREVER argument
    put_forever = bool(re.search(
        r'k_msgq_put\s*\([^)]*K_FOREVER[^)]*\)', generated_code
    ))
    details.append(
        CheckDetail(
            check_name="no_k_forever_in_msgq_put",
            passed=not put_forever,
            expected="K_FOREVER must NOT be used in k_msgq_put (ISR context)",
            actual="violation found" if put_forever else "clean",
            check_type="constraint",
        )
    )

    # Check 4: No k_malloc in ISR handler (forbidden)
    has_kmalloc = "k_malloc" in generated_code
    details.append(
        CheckDetail(
            check_name="no_kmalloc_in_isr",
            passed=not has_kmalloc,
            expected="No k_malloc (forbidden in ISR)",
            actual="k_malloc found" if has_kmalloc else "clean",
            check_type="constraint",
        )
    )

    # Check 5: Consumer thread defined (K_THREAD_DEFINE or k_thread_create)
    has_thread = (
        "K_THREAD_DEFINE" in generated_code
        or "k_thread_create" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="consumer_thread_defined",
            passed=has_thread,
            expected="Consumer thread defined with K_THREAD_DEFINE or k_thread_create",
            actual="present" if has_thread else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: No printk inside ISR handler
    # Heuristic: check if printk appears inside a function that has K_NO_WAIT
    # This is approximated by detecting printk near k_msgq_put
    isr_block = re.search(
        r'(isr_handler|ISR|irq_handler)\s*\([^{]*\)\s*\{([^}]*)\}',
        generated_code, re.IGNORECASE | re.DOTALL
    )
    isr_has_printk = False
    if isr_block:
        isr_has_printk = "printk" in isr_block.group(2)
    details.append(
        CheckDetail(
            check_name="no_printk_in_isr",
            passed=not isr_has_printk,
            expected="No printk inside ISR handler",
            actual="printk found in ISR" if isr_has_printk else "clean",
            check_type="constraint",
        )
    )

    return details
