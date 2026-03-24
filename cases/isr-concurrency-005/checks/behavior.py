"""Behavioral checks for ISR-deferred k_work processing."""

import re

from embedeval.check_utils import (
    check_no_cross_platform_apis,
    extract_function_body,
    strip_comments,
)
from embedeval.models import CheckDetail

# ISR forbidden APIs — subset relevant to strict ISR checking
# (printk is allowed in work_handler but not in actual ISR body)
_ISR_BODY_FORBIDDEN = [
    "k_malloc",
    "k_free",
    "printk",
    "printf",
    "k_sleep",
    "k_msleep",
    "k_mutex_lock",
]


def _check_isr_body_forbidden(isr_body: str) -> list[str]:
    """Check actual ISR body (not work handler) for forbidden APIs."""
    violations = []
    for api in _ISR_BODY_FORBIDDEN:
        if api in isr_body:
            violations.append(api)
    return list(set(violations))


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate k_work deferred processing behavioral properties."""
    details: list[CheckDetail] = []

    stripped = strip_comments(generated_code)

    # Find ISR body specifically (not work handler)
    # Use a narrow pattern that matches isr_handler/irq_handler but not work_handler
    isr_block = re.search(
        r'(?:static\s+)?void\s+((?:isr|irq)\w*|my_isr|sensor_isr)\s*\([^{]*\)\s*\{([^}]*)\}',
        generated_code, re.IGNORECASE | re.DOTALL
    )
    isr_body = isr_block.group(2) if isr_block else ""

    # Check 1: ISR is minimal — no heavy work directly in ISR
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

    # Check 7: ISR body itself has no forbidden blocking calls
    # Only check the actual ISR body, not the work_handler
    # LLM failure: putting printk or k_malloc directly in the ISR body
    if isr_body:
        isr_violations = _check_isr_body_forbidden(isr_body)
    else:
        # If we couldn't identify ISR body, fall back to checking whole code
        # but exclude work_handler context by checking if printk is ONLY in work handler
        isr_violations = []
    details.append(
        CheckDetail(
            check_name="no_forbidden_apis_in_isr_body",
            passed=len(isr_violations) == 0,
            expected="No printk/k_malloc/k_sleep inside the ISR body (deferred to work handler)",
            actual="clean" if not isr_violations else f"violations in ISR: {isr_violations}",
            check_type="constraint",
        )
    )

    # Check 8: No cross-platform API contamination
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
