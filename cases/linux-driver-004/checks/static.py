"""Static analysis checks for interrupt-driven character device driver."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate IRQ char device code structure."""
    details: list[CheckDetail] = []

    has_module_h = "linux/module.h" in generated_code
    details.append(
        CheckDetail(
            check_name="module_header",
            passed=has_module_h,
            expected="linux/module.h included",
            actual="present" if has_module_h else "missing",
            check_type="exact_match",
        )
    )

    has_interrupt_h = "linux/interrupt.h" in generated_code
    details.append(
        CheckDetail(
            check_name="interrupt_header",
            passed=has_interrupt_h,
            expected="linux/interrupt.h included",
            actual="present" if has_interrupt_h else "missing",
            check_type="exact_match",
        )
    )

    has_wait_h = "linux/wait.h" in generated_code
    details.append(
        CheckDetail(
            check_name="wait_header",
            passed=has_wait_h,
            expected="linux/wait.h included",
            actual="present" if has_wait_h else "missing",
            check_type="exact_match",
        )
    )

    has_spinlock_h = "linux/spinlock.h" in generated_code
    details.append(
        CheckDetail(
            check_name="spinlock_header",
            passed=has_spinlock_h,
            expected="linux/spinlock.h included",
            actual="present" if has_spinlock_h else "missing",
            check_type="exact_match",
        )
    )

    has_request_irq = "request_irq" in generated_code
    details.append(
        CheckDetail(
            check_name="request_irq_called",
            passed=has_request_irq,
            expected="request_irq() called in init",
            actual="present" if has_request_irq else "missing",
            check_type="exact_match",
        )
    )

    has_irq_handler = "irqreturn_t" in generated_code
    details.append(
        CheckDetail(
            check_name="irq_handler_defined",
            passed=has_irq_handler,
            expected="IRQ handler with irqreturn_t signature",
            actual="present" if has_irq_handler else "missing",
            check_type="exact_match",
        )
    )

    has_wait_queue = (
        "wait_queue_head_t" in generated_code
        or "DECLARE_WAIT_QUEUE_HEAD" in generated_code
        or "init_waitqueue_head" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="wait_queue_declared",
            passed=has_wait_queue,
            expected="wait_queue_head_t declared and initialized",
            actual="present" if has_wait_queue else "missing",
            check_type="exact_match",
        )
    )

    return details
