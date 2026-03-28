"""Behavioral checks for nested interrupt priority management."""

import re

from embedeval.check_utils import (
    check_no_cross_platform_apis,
    check_no_isr_forbidden,
    find_isr_bodies,
    strip_comments,
)
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate ISR bodies and priority semantics."""
    details: list[CheckDetail] = []

    stripped = strip_comments(generated_code)

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

    # Check 2: No k_sleep inside any ISR body — using check_utils find_isr_bodies
    isr_bodies = find_isr_bodies(stripped)
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

    # Check 6: No forbidden blocking ISR APIs (using check_utils for thorough check)
    # The printk check is intentionally skipped here since the reference uses
    # printk in ISR as "observable work" — but k_malloc/k_sleep should not appear
    isr_violations = check_no_isr_forbidden(generated_code)
    # Filter out printk violations since this case legitimately uses printk in ISR
    non_printk_violations = [v for v in isr_violations if "printk" not in v and "printf" not in v]
    details.append(
        CheckDetail(
            check_name="no_blocking_forbidden_in_isr",
            passed=len(non_printk_violations) == 0,
            expected="No k_malloc/k_sleep/k_mutex_lock inside ISR bodies",
            actual="clean" if not non_printk_violations else f"violations: {non_printk_violations}",
            check_type="constraint",
        )
    )

    # Check 7: No cross-platform API contamination
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

    # Check 8: High-priority IRQ must have the LOWER numeric priority value (ARM convention)
    # LLM failure: setting HIGH_PRIORITY = 5, LOW_PRIORITY = 1 (backwards)
    prio_defines = re.findall(
        r'#define\s+(\w*(?:HIGH|LOW|FAST|SLOW)\w*(?:PRIO|PRIORITY|LEVEL)\w*)\s+(\d+)',
        generated_code, re.IGNORECASE
    )
    if len(prio_defines) >= 2:
        high_entries = [
            (name, int(val)) for name, val in prio_defines
            if re.search(r'HIGH|FAST|CRITICAL', name, re.IGNORECASE)
        ]
        low_entries = [
            (name, int(val)) for name, val in prio_defines
            if re.search(r'LOW|SLOW|BACKGROUND', name, re.IGNORECASE)
        ]
        if high_entries and low_entries:
            min_high = min(v for _, v in high_entries)
            min_low = min(v for _, v in low_entries)
            priority_correct = min_high < min_low
            actual_prio_msg = (
                f"correct: {high_entries[0][0]}={min_high} < {low_entries[0][0]}={min_low}"
                if priority_correct
                else f"BACKWARDS: {high_entries[0][0]}={min_high} >= {low_entries[0][0]}={min_low} (lower number = higher priority on ARM)"
            )
        else:
            # Fall back to IRQ_CONNECT priority params if defines aren't clearly named
            irq_connect_params = re.findall(
                r'IRQ_CONNECT\s*\(\s*\w+\s*,\s*(\d+)\s*,', generated_code
            )
            if len(irq_connect_params) >= 2:
                vals = [int(v) for v in irq_connect_params]
                priority_correct = vals[0] < vals[1]
                actual_prio_msg = (
                    f"IRQ_CONNECT priorities: {vals} — first handler has lower (higher-priority) number"
                    if priority_correct
                    else f"IRQ_CONNECT priorities: {vals} — first handler has higher number (may be backwards)"
                )
            else:
                priority_correct = False
                actual_prio_msg = "found HIGH/LOW defines but could not determine which is which"
    elif prio_defines:
        priority_correct = False
        actual_prio_msg = f"only one priority #define found: {prio_defines} — cannot verify ordering"
    else:
        # No #define found — check IRQ_CONNECT directly
        irq_connect_params = re.findall(
            r'IRQ_CONNECT\s*\(\s*\w+\s*,\s*(\d+)\s*,', generated_code
        )
        if len(irq_connect_params) >= 2:
            vals = [int(v) for v in irq_connect_params]
            # Cannot determine which is "high" without names; mark as not confirmed
            priority_correct = False
            actual_prio_msg = f"IRQ_CONNECT priorities found: {vals} — no named defines to verify ordering"
        else:
            priority_correct = False
            actual_prio_msg = "no priority #defines or IRQ_CONNECT priority params found"
    details.append(
        CheckDetail(
            check_name="high_priority_lower_number",
            passed=priority_correct,
            expected="High-priority IRQ has lower numeric value (ARM: lower number = higher priority)",
            actual=actual_prio_msg,
            check_type="constraint",
        )
    )

    # Check: IRQ priority explicitly configured
    has_irq_config = bool(re.search(r'IRQ_CONNECT\s*\(', generated_code)) or \
                     bool(re.search(r'irq_connect_dynamic\s*\(', generated_code))
    details.append(CheckDetail(
        check_name="irq_priority_configured",
        passed=has_irq_config,
        expected="IRQ_CONNECT or irq_connect_dynamic used with priority parameter",
        actual="IRQ priority configured" if has_irq_config else "no IRQ priority configuration",
        check_type="constraint",
    ))

    return details
