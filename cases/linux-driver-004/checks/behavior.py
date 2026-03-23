"""Behavioral checks for interrupt-driven character device driver."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate IRQ char device behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: free_irq called in exit (balances request_irq in init)
    # (LLM failure: request_irq in init, no free_irq in exit = use-after-free)
    has_free_irq = "free_irq" in generated_code
    details.append(
        CheckDetail(
            check_name="free_irq_in_exit",
            passed=has_free_irq,
            expected="free_irq() called in module_exit to balance request_irq",
            actual="present" if has_free_irq else "MISSING (IRQ leak on unload!)",
            check_type="constraint",
        )
    )

    # Check 2: spin_lock used in IRQ handler (not mutex — mutex can sleep)
    # (LLM failure: using mutex_lock inside IRQ handler causes BUG: scheduling while atomic)
    has_spinlock = (
        "spin_lock" in generated_code
        or "DEFINE_SPINLOCK" in generated_code
        or "DEFINE_SPINLOCK" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="spinlock_in_irq_handler",
            passed=has_spinlock,
            expected="spin_lock used in IRQ handler (mutex cannot be used in IRQ context)",
            actual="present" if has_spinlock else "MISSING or using mutex (sleep in IRQ!)",
            check_type="constraint",
        )
    )

    # Check 3: wait_event_interruptible used in read (blocks until IRQ fires)
    # (LLM failure: busy-polling with while(data_ready==0) burns CPU)
    has_wait_event = "wait_event_interruptible" in generated_code
    details.append(
        CheckDetail(
            check_name="wait_event_interruptible_in_read",
            passed=has_wait_event,
            expected="wait_event_interruptible() in read() for blocking wait",
            actual="present" if has_wait_event else "missing (busy-poll or no wait?)",
            check_type="constraint",
        )
    )

    # Check 4: wake_up_interruptible called from IRQ handler
    # (LLM failure: wakes wrong queue or never wakes reader)
    has_wake_up = "wake_up_interruptible" in generated_code
    details.append(
        CheckDetail(
            check_name="wake_up_interruptible_in_handler",
            passed=has_wake_up,
            expected="wake_up_interruptible() called from IRQ handler",
            actual="present" if has_wake_up else "MISSING (reader never unblocks!)",
            check_type="constraint",
        )
    )

    # Check 5: IRQ_HANDLED returned from handler (not IRQ_NONE or 0)
    # (LLM failure: returning 0/void from IRQ handler)
    has_irq_handled = "IRQ_HANDLED" in generated_code
    details.append(
        CheckDetail(
            check_name="irq_handled_returned",
            passed=has_irq_handled,
            expected="IRQ_HANDLED returned from IRQ handler",
            actual="present" if has_irq_handled else "missing",
            check_type="constraint",
        )
    )

    # Check 6: copy_to_user used (not direct pointer access in read)
    has_copy_to = "copy_to_user" in generated_code
    details.append(
        CheckDetail(
            check_name="copy_to_user_in_read",
            passed=has_copy_to,
            expected="copy_to_user() for kernel→user transfer in read()",
            actual="present" if has_copy_to else "MISSING (security!)",
            check_type="constraint",
        )
    )

    return details
