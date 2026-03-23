"""Behavioral checks for nested interrupt priority management."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate ISR bodies and priority semantics."""
    details: list[CheckDetail] = []

    # Check 1: Two distinct ISR functions defined
    isr_fns = re.findall(
        r"(?:static\s+)?void\s+(\w*(?:isr|irq|interrupt|handler)\w*)\s*\([^)]*\)",
        generated_code,
        re.IGNORECASE,
    )
    has_two_isrs = len(isr_fns) >= 2
    details.append(
        CheckDetail(
            check_name="two_isr_functions",
            passed=has_two_isrs,
            expected="Two ISR handler functions defined",
            actual=f"isr functions={isr_fns}",
            check_type="exact_match",
        )
    )

    # Check 2: No k_sleep inside any ISR body
    # Extract ISR-like function bodies and check for blocking calls
    isr_body_pattern = re.compile(
        r"void\s+\w*(?:isr|irq|interrupt|handler)\w*\s*\([^)]*\)\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}",
        re.IGNORECASE | re.DOTALL,
    )
    isr_bodies = isr_body_pattern.findall(generated_code)
    isr_has_sleep = any(
        "k_sleep" in body or "k_msleep" in body or "k_usleep" in body
        for body in isr_bodies
    )
    details.append(
        CheckDetail(
            check_name="no_sleep_in_isr",
            passed=not isr_has_sleep,
            expected="No k_sleep/k_msleep in ISR bodies",
            actual="sleep in ISR (BUG)" if isr_has_sleep else "clean",
            check_type="constraint",
        )
    )

    # Check 3: No k_mutex/k_sem operations in ISR bodies
    isr_has_mutex = any(
        "k_mutex_lock" in body or "k_sem_take" in body
        for body in isr_bodies
    )
    details.append(
        CheckDetail(
            check_name="no_blocking_sync_in_isr",
            passed=not isr_has_mutex,
            expected="No k_mutex_lock or k_sem_take in ISR bodies",
            actual="blocking sync in ISR (BUG)" if isr_has_mutex else "clean",
            check_type="constraint",
        )
    )

    # Check 4: IRQ_CONNECT or irq_connect_dynamic used (not raw function pointer assignment)
    has_irq_connect = "IRQ_CONNECT" in generated_code or "irq_connect_dynamic" in generated_code
    details.append(
        CheckDetail(
            check_name="uses_irq_connect",
            passed=has_irq_connect,
            expected="IRQ_CONNECT or irq_connect_dynamic used to register ISRs",
            actual="present" if has_irq_connect else "missing (raw assignment?)",
            check_type="exact_match",
        )
    )

    # Check 5: Both ISRs print something (short observable work, not empty)
    has_printk_in_isrs = generated_code.count("printk") >= 2
    details.append(
        CheckDetail(
            check_name="isrs_have_observable_work",
            passed=has_printk_in_isrs,
            expected="Both ISR bodies do observable work (printk)",
            actual=f"printk count={generated_code.count('printk')}",
            check_type="constraint",
        )
    )

    return details
