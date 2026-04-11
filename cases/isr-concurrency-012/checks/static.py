"""Static checks for isr-concurrency-012: correct ISR-safe sync primitive."""

import re

from embedeval.models import CheckDetail


def _strip_comments(code: str) -> str:
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
    code = re.sub(r"//[^\n]*", "", code)
    return code


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []
    stripped = _strip_comments(generated_code)

    has_kernel_h = "zephyr/kernel.h" in generated_code
    details.append(
        CheckDetail(
            check_name="kernel_header",
            passed=has_kernel_h,
            expected="zephyr/kernel.h included",
            actual="present" if has_kernel_h else "missing",
            check_type="exact_match",
        )
    )

    # Correct sync primitive: k_spinlock
    uses_spinlock = "k_spinlock" in stripped or "k_spin_lock" in stripped
    details.append(
        CheckDetail(
            check_name="uses_spinlock",
            passed=uses_spinlock,
            expected="k_spinlock / k_spin_lock used as ISR-safe sync",
            actual="present" if uses_spinlock else "missing",
            check_type="constraint",
        )
    )

    # Forbidden ISR-unsafe primitives: k_mutex, k_sem_take (blocking), irq_lock
    forbidden = []
    if re.search(r"\bk_mutex\b", stripped):
        forbidden.append("k_mutex")
    if "irq_lock(" in stripped or "irq_unlock(" in stripped:
        forbidden.append("irq_lock/unlock")
    if re.search(r"\bk_sem_take\s*\(", stripped):
        forbidden.append("k_sem_take")

    details.append(
        CheckDetail(
            check_name="no_isr_unsafe_primitives",
            passed=len(forbidden) == 0,
            expected="No k_mutex / irq_lock / k_sem_take (ISR-unsafe or suboptimal)",
            actual="clean" if not forbidden else f"found: {forbidden}",
            check_type="constraint",
        )
    )

    # Spinlock key captured and passed to unlock
    has_key_var = bool(
        re.search(
            r"(?:k_spinlock_key_t\s+\w+|\b\w+\s*=\s*k_spin_lock\s*\()",
            stripped,
        )
    )
    details.append(
        CheckDetail(
            check_name="spinlock_key_saved",
            passed=has_key_var,
            expected="k_spinlock_key_t variable holds k_spin_lock() return",
            actual="present" if has_key_var else "missing (IRQ key lost)",
            check_type="constraint",
        )
    )

    # irq_offload used as ISR trigger
    has_irq_offload = "irq_offload" in generated_code
    details.append(
        CheckDetail(
            check_name="irq_offload_used",
            passed=has_irq_offload,
            expected="irq_offload() used to simulate ISR",
            actual="present" if has_irq_offload else "missing",
            check_type="exact_match",
        )
    )

    # Paired lock/unlock in both ISR and thread
    lock_count = stripped.count("k_spin_lock")
    unlock_count = stripped.count("k_spin_unlock")
    balanced = lock_count >= 2 and lock_count == unlock_count
    details.append(
        CheckDetail(
            check_name="lock_unlock_balanced_both_contexts",
            passed=balanced,
            expected="k_spin_lock/unlock called >=2 times and balanced (ISR + thread)",
            actual=f"lock={lock_count}, unlock={unlock_count}",
            check_type="constraint",
        )
    )

    return details
