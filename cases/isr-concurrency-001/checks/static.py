"""Static analysis checks for ISR-safe ring buffer implementation."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate ISR context safety rules for ring buffer code."""
    details: list[CheckDetail] = []

    # Check 1: No k_malloc usage (forbidden in ISR)
    has_kmalloc = "k_malloc" in generated_code
    details.append(
        CheckDetail(
            check_name="no_kmalloc",
            passed=not has_kmalloc,
            expected="No k_malloc calls (forbidden in ISR)",
            actual="k_malloc found" if has_kmalloc else "no k_malloc",
            check_type="constraint",
        )
    )

    # Check 2: No floating point operations
    fp_keywords = ["float", "double", "%.f", "%f"]
    has_fp = any(kw in generated_code for kw in fp_keywords)
    details.append(
        CheckDetail(
            check_name="no_floating_point",
            passed=not has_fp,
            expected="No floating point operations (ISR context)",
            actual="floating point found" if has_fp else "no floating point",
            check_type="constraint",
        )
    )

    # Check 3: No printk usage
    has_printk = "printk" in generated_code
    details.append(
        CheckDetail(
            check_name="no_printk",
            passed=not has_printk,
            expected="No printk calls (ISR context)",
            actual="printk found" if has_printk else "no printk",
            check_type="constraint",
        )
    )

    # Check 4: Uses atomic operations
    atomic_patterns = ["atomic_t", "atomic_set", "atomic_get"]
    has_atomic = any(p in generated_code for p in atomic_patterns)
    details.append(
        CheckDetail(
            check_name="uses_atomic_operations",
            passed=has_atomic,
            expected="Uses atomic_t, atomic_set, or atomic_get",
            actual="atomic operations found" if has_atomic else "no atomic operations",
            check_type="exact_match",
        )
    )

    # Check 5: Includes zephyr headers
    zephyr_headers = ["zephyr/kernel.h", "zephyr/sys/atomic.h"]
    has_zephyr = any(h in generated_code for h in zephyr_headers)
    details.append(
        CheckDetail(
            check_name="zephyr_headers_included",
            passed=has_zephyr,
            expected="Zephyr kernel or atomic headers included",
            actual="zephyr headers found" if has_zephyr else "no zephyr headers",
            check_type="exact_match",
        )
    )

    return details
