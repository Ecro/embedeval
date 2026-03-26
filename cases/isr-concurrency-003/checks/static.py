"""Static analysis checks for spinlock-protected shared state."""

import re

from embedeval.models import CheckDetail


def _strip_comments(code: str) -> str:
    """Remove C block comments and line comments to avoid false matches."""
    # Remove /* ... */ block comments
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    # Remove // line comments
    code = re.sub(r'//[^\n]*', '', code)
    return code


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate spinlock ISR safety constraints."""
    details: list[CheckDetail] = []
    code_no_comments = _strip_comments(generated_code)

    # Check 1: k_spinlock used (not k_mutex which is forbidden in ISR)
    has_spinlock = "k_spinlock" in code_no_comments or "K_SPINLOCK_DEFINE" in code_no_comments
    details.append(
        CheckDetail(
            check_name="k_spinlock_used",
            passed=has_spinlock,
            expected="k_spinlock or K_SPINLOCK_DEFINE used",
            actual="present" if has_spinlock else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: k_mutex / irq_lock / irq_unlock NOT used in code.
    # k_mutex is forbidden in ISR context. irq_lock/irq_unlock globally disable interrupts —
    # worse than spinlock and still incorrect for this pattern (LLM blind spot).
    # Search only in comment-stripped code to avoid false matches in comments.
    forbidden = ["k_mutex", "irq_lock(", "irq_unlock("]
    found_forbidden = [f for f in forbidden if f in code_no_comments]
    # Also match k_mutex via word boundary to catch k_mutex_lock / k_mutex_unlock variants
    if not found_forbidden and bool(re.search(r'\bk_mutex\b', code_no_comments)):
        found_forbidden.append("k_mutex")
    has_forbidden = len(found_forbidden) > 0
    details.append(
        CheckDetail(
            check_name="no_k_mutex",
            passed=not has_forbidden,
            expected="No k_mutex / irq_lock / irq_unlock (all forbidden; use k_spinlock)",
            actual=f"found: {found_forbidden}" if has_forbidden else "clean",
            check_type="constraint",
        )
    )

    # Check 3: k_spin_lock called
    has_lock = "k_spin_lock" in generated_code
    details.append(
        CheckDetail(
            check_name="k_spin_lock_called",
            passed=has_lock,
            expected="k_spin_lock() called",
            actual="present" if has_lock else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: k_spinlock_key_t used (IRQ key saved — LLM failure: not saving key)
    has_key_type = "k_spinlock_key_t" in generated_code
    details.append(
        CheckDetail(
            check_name="spinlock_key_saved",
            passed=has_key_type,
            expected="k_spinlock_key_t used to save IRQ key",
            actual="present" if has_key_type else "missing (IRQ key not saved — context lost!)",
            check_type="constraint",
        )
    )

    # Check 5: k_spin_unlock called (key must be restored)
    has_unlock = "k_spin_unlock" in generated_code
    details.append(
        CheckDetail(
            check_name="k_spin_unlock_called",
            passed=has_unlock,
            expected="k_spin_unlock() called to restore IRQ key",
            actual="present" if has_unlock else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: Shared variable declared globally or statically
    has_shared_var = bool(re.search(
        r'\b(static|volatile)?\s*uint\d+_t\s+\w+(counter|shared|data)\w*\s*[;=]',
        generated_code, re.IGNORECASE
    ))
    details.append(
        CheckDetail(
            check_name="shared_variable_declared",
            passed=has_shared_var,
            expected="Shared variable (counter/data) declared",
            actual="present" if has_shared_var else "missing",
            check_type="constraint",
        )
    )

    return details
