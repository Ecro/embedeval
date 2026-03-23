"""Static analysis checks for lock-free SPSC ring queue."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate lock-free SPSC queue constraints."""
    details: list[CheckDetail] = []

    # Check 1: atomic.h or kernel.h included
    has_atomic_h = "zephyr/sys/atomic.h" in generated_code or "zephyr/kernel.h" in generated_code
    details.append(
        CheckDetail(
            check_name="atomic_header_included",
            passed=has_atomic_h,
            expected="zephyr/sys/atomic.h or zephyr/kernel.h included",
            actual="present" if has_atomic_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: No k_mutex, k_sem, or k_spin_lock (must be lock-free)
    locking_apis = ["k_mutex", "k_sem_take", "k_sem_give", "k_spin_lock", "k_spin_unlock"]
    has_locking = any(api in generated_code for api in locking_apis)
    details.append(
        CheckDetail(
            check_name="no_locking_primitives",
            passed=not has_locking,
            expected="No k_mutex, k_sem, or k_spin_lock (lock-free design)",
            actual="locking primitive found" if has_locking else "lock-free confirmed",
            check_type="constraint",
        )
    )

    # Check 3: atomic_t used for indices
    has_atomic_t = "atomic_t" in generated_code
    details.append(
        CheckDetail(
            check_name="atomic_t_for_indices",
            passed=has_atomic_t,
            expected="atomic_t used for read/write indices",
            actual="present" if has_atomic_t else "missing (plain int?)",
            check_type="exact_match",
        )
    )

    # Check 4: atomic_get and atomic_set used
    has_atomic_ops = "atomic_get" in generated_code and "atomic_set" in generated_code
    details.append(
        CheckDetail(
            check_name="atomic_get_set_used",
            passed=has_atomic_ops,
            expected="Both atomic_get() and atomic_set() used",
            actual="present" if has_atomic_ops else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Power-of-2 buffer size (check for 2, 4, 8, 16, 32, 64, 128, 256)
    pow2_sizes = re.findall(r"\b(2|4|8|16|32|64|128|256|512|1024)\b", generated_code)
    # Also look for buffer size defines
    size_define = re.search(r"#define\s+\w*(?:SIZE|BUF|LEN|DEPTH)\w*\s+(\d+)", generated_code)
    size_val = int(size_define.group(1)) if size_define else 0
    is_pow2 = size_val > 0 and (size_val & (size_val - 1)) == 0
    details.append(
        CheckDetail(
            check_name="power_of_2_size",
            passed=is_pow2 or len(pow2_sizes) > 0,
            expected="Buffer size is a power of 2 (enables bitwise masking)",
            actual=f"size={size_val}" if size_define else "no #define size found",
            check_type="constraint",
        )
    )

    # Check 6: Bitwise mask used (& (SIZE-1) or & MASK_CONSTANT) instead of modulo %
    # Accept explicit (& (SIZE-1)) pattern or a named MASK constant used with &
    has_explicit_bitmask = bool(re.search(r"&\s*\(\s*\w+\s*-\s*1\s*\)", generated_code))
    # Also accept a #define MASK (SIZE-1) pattern with the mask used via &
    mask_define = re.search(
        r"#define\s+\w*MASK\w*\s*\(?\s*\w+\s*-\s*1\s*\)?",
        generated_code,
        re.IGNORECASE,
    )
    mask_used = bool(re.search(r"&\s*\w*MASK\w*", generated_code, re.IGNORECASE))
    has_bitmask = has_explicit_bitmask or (mask_define is not None and mask_used)
    details.append(
        CheckDetail(
            check_name="bitwise_mask_not_modulo",
            passed=has_bitmask,
            expected="Bitwise mask (& (SIZE-1) or & MASK constant) used instead of modulo %",
            actual="bitmask found" if has_bitmask else "no bitmask (modulo?)",
            check_type="constraint",
        )
    )

    return details
