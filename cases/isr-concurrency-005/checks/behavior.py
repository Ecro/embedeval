"""Behavioral checks for ISR-deferred k_work processing."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate k_work deferred processing behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: ISR is minimal — no heavy work directly in ISR
    # Heavy work indicators: for loops with printk, lengthy computation
    isr_block = re.search(
        r'(isr_handler|ISR|irq_handler)\s*\([^{]*\)\s*\{([^}]*)\}',
        generated_code, re.IGNORECASE | re.DOTALL
    )
    isr_body = isr_block.group(2) if isr_block else ""
    isr_has_heavy_work = bool(re.search(
        r'\bfor\s*\(|\bwhile\s*\(|\bprintk\b', isr_body
    ))
    details.append(
        CheckDetail(
            check_name="isr_is_minimal",
            passed=not isr_has_heavy_work,
            expected="ISR does minimal work (no loops, no printk)",
            actual="ISR has heavy work!" if isr_has_heavy_work else "minimal",
            check_type="constraint",
        )
    )

    # Check 2: k_work_submit inside ISR (deferred, not direct call)
    isr_submits = "k_work_submit" in isr_body if isr_body else False
    details.append(
        CheckDetail(
            check_name="isr_submits_work",
            passed=isr_submits,
            expected="ISR calls k_work_submit() to defer processing",
            actual="present" if isr_submits else "missing",
            check_type="constraint",
        )
    )

    # Check 3: Work handler does the actual processing (has printk or computation)
    # Find work handler function body
    work_handler_block = re.search(
        r'(work_handler|process_work|deferred_work)\s*\([^{]*\)\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}',
        generated_code, re.IGNORECASE | re.DOTALL
    )
    work_body = work_handler_block.group(2) if work_handler_block else ""
    work_has_processing = bool(re.search(
        r'\bprintk\b|\bfor\s*\(|\bwhile\s*\(|\bsum\b|\bprocess\b',
        work_body, re.IGNORECASE
    ))
    details.append(
        CheckDetail(
            check_name="work_handler_does_processing",
            passed=work_has_processing,
            expected="Work handler performs actual processing (loops, printk, etc.)",
            actual="present" if work_has_processing else "missing (empty handler?)",
            check_type="constraint",
        )
    )

    # Check 4: Event counter incremented atomically in ISR
    has_atomic_inc = bool(re.search(
        r'atomic_inc|atomic_add|atomic_set\s*\([^,]+,\s*atomic_get',
        isr_body
    ))
    details.append(
        CheckDetail(
            check_name="atomic_counter_in_isr",
            passed=has_atomic_inc,
            expected="ISR increments event counter atomically (atomic_inc/atomic_add)",
            actual="present" if has_atomic_inc else "missing (non-atomic counter race)",
            check_type="constraint",
        )
    )

    # Check 5: k_sleep in main to allow work queue to drain
    has_sleep = "k_sleep" in generated_code
    details.append(
        CheckDetail(
            check_name="k_sleep_for_drain",
            passed=has_sleep,
            expected="k_sleep() in main to allow work queue to drain",
            actual="present" if has_sleep else "missing (work may not execute before exit)",
            check_type="constraint",
        )
    )

    # Check 6: Work item not accessed after submit without sync
    # Heuristic: check if code accesses work item members after k_work_submit
    # (simplified: just check there's no dereference of work struct post-submit)
    has_post_submit_access = bool(re.search(
        r'k_work_submit[^;]+;[^}]*my_work\.',
        generated_code, re.DOTALL
    ))
    details.append(
        CheckDetail(
            check_name="no_work_access_after_submit",
            passed=not has_post_submit_access,
            expected="Work item not accessed after submit without synchronization",
            actual="violation found" if has_post_submit_access else "clean",
            check_type="constraint",
        )
    )

    return details
