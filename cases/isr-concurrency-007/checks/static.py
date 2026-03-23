"""Static analysis checks for nested interrupt priority management."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate nested IRQ priority configuration."""
    details: list[CheckDetail] = []

    # Check 1: zephyr/irq.h or zephyr/kernel.h present
    has_irq_h = "zephyr/irq.h" in generated_code or "zephyr/kernel.h" in generated_code
    details.append(
        CheckDetail(
            check_name="irq_header_included",
            passed=has_irq_h,
            expected="zephyr/irq.h or zephyr/kernel.h included",
            actual="present" if has_irq_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: Two different priority values used
    # Collect the priority argument (literal or identifier) from IRQ_CONNECT calls
    import re
    priority_vals = re.findall(
        r"IRQ_CONNECT\s*\([^,]+,\s*(\w+)\s*,",
        generated_code,
    )
    if not priority_vals:
        priority_vals = re.findall(
            r"irq_connect_dynamic\s*\([^,]+,\s*(\w+)\s*,",
            generated_code,
        )
    # Resolve macro names to their defined values where possible
    resolved = []
    for val in priority_vals:
        macro_match = re.search(
            r"#define\s+" + re.escape(val) + r"\s+(\d+)",
            generated_code,
        )
        resolved.append(macro_match.group(1) if macro_match else val)
    priorities_differ = len(set(resolved)) >= 2 if resolved else False
    details.append(
        CheckDetail(
            check_name="priorities_are_different",
            passed=priorities_differ,
            expected="Two IRQs configured with different priority values",
            actual=f"priorities={resolved}" if resolved else "no IRQ_CONNECT found",
            check_type="constraint",
        )
    )

    # Check 3: irq_lock/irq_unlock NOT used for priority management
    # (Wrong approach — these globally disable ALL interrupts)
    has_irq_lock = "irq_lock()" in generated_code or "irq_unlock(" in generated_code
    details.append(
        CheckDetail(
            check_name="no_irq_lock_for_priority",
            passed=not has_irq_lock,
            expected="No irq_lock/irq_unlock (use priority levels instead)",
            actual="irq_lock found" if has_irq_lock else "clean",
            check_type="constraint",
        )
    )

    # Check 4: irq_enable called for both ISRs
    enable_count = generated_code.count("irq_enable(")
    details.append(
        CheckDetail(
            check_name="both_irqs_enabled",
            passed=enable_count >= 2,
            expected="irq_enable() called at least twice (one per IRQ)",
            actual=f"irq_enable count={enable_count}",
            check_type="constraint",
        )
    )

    # Check 5: No POSIX scheduling APIs
    posix_apis = ["pthread_setschedprio", "sched_setscheduler", "pthread_attr_setschedparam"]
    has_posix = any(api in generated_code for api in posix_apis)
    details.append(
        CheckDetail(
            check_name="no_posix_sched_apis",
            passed=not has_posix,
            expected="No POSIX scheduling APIs",
            actual="POSIX API found" if has_posix else "clean",
            check_type="constraint",
        )
    )

    return details
