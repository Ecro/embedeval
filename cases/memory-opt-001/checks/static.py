"""Static analysis checks for memory slab allocation."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate memory slab code structure."""
    details: list[CheckDetail] = []

    # Check 1: kernel header
    has_kernel_h = "zephyr/kernel.h" in generated_code
    details.append(
        CheckDetail(
            check_name="kernel_header_included",
            passed=has_kernel_h,
            expected="zephyr/kernel.h included",
            actual="present" if has_kernel_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: K_MEM_SLAB_DEFINE used
    has_slab = "K_MEM_SLAB_DEFINE" in generated_code
    details.append(
        CheckDetail(
            check_name="mem_slab_defined",
            passed=has_slab,
            expected="K_MEM_SLAB_DEFINE macro used",
            actual="present" if has_slab else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: k_mem_slab_alloc used
    has_alloc = "k_mem_slab_alloc" in generated_code
    details.append(
        CheckDetail(
            check_name="slab_alloc_called",
            passed=has_alloc,
            expected="k_mem_slab_alloc() called",
            actual="present" if has_alloc else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: k_mem_slab_free used
    has_free = "k_mem_slab_free" in generated_code
    details.append(
        CheckDetail(
            check_name="slab_free_called",
            passed=has_free,
            expected="k_mem_slab_free() called",
            actual="present" if has_free else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: NO heap allocation (malloc, calloc, k_malloc)
    heap_funcs = ["malloc(", "calloc(", "k_malloc(", "k_calloc("]
    has_heap = any(f in generated_code for f in heap_funcs)
    details.append(
        CheckDetail(
            check_name="no_heap_allocation",
            passed=not has_heap,
            expected="No malloc/calloc/k_malloc (heap-free)",
            actual="heap alloc found" if has_heap else "heap-free",
            check_type="constraint",
        )
    )

    return details
