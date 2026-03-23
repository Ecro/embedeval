"""Behavioral checks for hardware counter precise timing application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate hardware counter behavioral properties and ISR constraints."""
    details: list[CheckDetail] = []

    # Check 1: counter_start before alarm setup
    start_pos = generated_code.find("counter_start")
    alarm_pos = generated_code.find("counter_set_channel_alarm")
    order_ok = start_pos != -1 and alarm_pos != -1 and start_pos < alarm_pos
    details.append(
        CheckDetail(
            check_name="counter_start_before_alarm",
            passed=order_ok,
            expected="counter_start() called before counter_set_channel_alarm()",
            actual="correct order" if order_ok else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: ISR/callback is non-blocking — no k_sleep in callback body
    # Heuristic: find callback function, check if k_sleep appears inside it
    # Simple check: if k_sleep appears immediately after the callback signature
    import re
    callback_body = re.search(
        r"(alarm_callback|counter_callback|cb)\s*\([^)]*\)\s*\{([^}]*)\}", generated_code
    )
    isr_has_sleep = False
    if callback_body:
        isr_body = callback_body.group(2)
        isr_has_sleep = "k_sleep" in isr_body or "printk" in isr_body
    details.append(
        CheckDetail(
            check_name="isr_non_blocking",
            passed=not isr_has_sleep,
            expected="Alarm callback is non-blocking (no k_sleep or printk)",
            actual="blocking call in ISR" if isr_has_sleep else "non-blocking",
            check_type="constraint",
        )
    )

    # Check 3: Elapsed time calculated (subtraction of two counter values)
    has_elapsed = "-" in generated_code and "ticks" in generated_code.lower()
    details.append(
        CheckDetail(
            check_name="elapsed_ticks_calculated",
            passed=has_elapsed,
            expected="Elapsed ticks calculated as difference of two counter reads",
            actual="present" if has_elapsed else "missing",
            check_type="constraint",
        )
    )

    # Check 4: device_is_ready check present
    has_ready = "device_is_ready" in generated_code
    details.append(
        CheckDetail(
            check_name="device_ready_check",
            passed=has_ready,
            expected="device_is_ready() called for counter device",
            actual="present" if has_ready else "missing",
            check_type="constraint",
        )
    )

    # Check 5: counter_get_value called at least twice (before and after)
    get_count = generated_code.count("counter_get_value")
    two_reads = get_count >= 2
    details.append(
        CheckDetail(
            check_name="counter_read_twice",
            passed=two_reads,
            expected="counter_get_value() called at least twice for measurement",
            actual=f"counter_get_value called {get_count} time(s)",
            check_type="constraint",
        )
    )

    # Check 6: Real-time constraint — no unbounded busy-wait loop as timing mechanism
    has_busy_wait_timing = bool(re.search(r"while\s*\(\s*!\s*alarm_ticks\s*\)", generated_code))
    details.append(
        CheckDetail(
            check_name="no_busy_wait_for_timing",
            passed=not has_busy_wait_timing,
            expected="k_sleep used to wait for alarm, not busy-wait polling",
            actual="busy-wait found" if has_busy_wait_timing else "clean",
            check_type="constraint",
        )
    )

    return details
