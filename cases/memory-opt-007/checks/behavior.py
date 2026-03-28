"""Behavioral checks for fixed-size object pool pattern."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate object pool behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: No malloc/calloc/k_malloc
    heap_funcs = ["malloc(", "calloc(", "k_malloc(", "k_calloc("]
    has_heap = any(f in generated_code for f in heap_funcs)
    details.append(
        CheckDetail(
            check_name="no_heap_in_pool_impl",
            passed=not has_heap,
            expected="No heap allocation functions (malloc/calloc/k_malloc)",
            actual="heap-free" if not has_heap else "VIOLATION: heap found in pool implementation",
            check_type="constraint",
        )
    )

    # Check 2: Static array defined at compile time
    has_static = "static" in generated_code and (
        "[POOL_SIZE]" in generated_code
        or "[8]" in generated_code
        or "[16]" in generated_code
        or "[4]" in generated_code
        or "pool[" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="compile_time_static_array",
            passed=has_static,
            expected="Static array defined at compile time (not runtime)",
            actual="present" if has_static else "missing",
            check_type="constraint",
        )
    )

    # Check 3: Free list or bitmap tracking allocations
    has_freelist = (
        "free_next" in generated_code
        or "free_list" in generated_code
        or "free_head" in generated_code
        or "in_use" in generated_code
        or "bitmap" in generated_code
        or "used[" in generated_code
        or "available[" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="free_list_or_bitmap_tracking",
            passed=has_freelist,
            expected="Free list or bitmap used to track available pool slots",
            actual="present" if has_freelist else "missing (how are free slots tracked?)",
            check_type="constraint",
        )
    )

    # Check 4: alloc and free are both implemented (balanced interface)
    has_alloc = "_alloc" in generated_code
    has_free = "_free" in generated_code
    details.append(
        CheckDetail(
            check_name="alloc_and_free_both_implemented",
            passed=has_alloc and has_free,
            expected="Both alloc and free functions implemented",
            actual=f"alloc={has_alloc}, free={has_free}",
            check_type="constraint",
        )
    )

    # Check 5: Bounds validation in free function
    has_bounds_check = (
        ">= &pool" in generated_code
        or "< pool" in generated_code
        or "< &pool" in generated_code
        or ">= pool" in generated_code
        or "obj <" in generated_code
        or "obj >" in generated_code
        or "within" in generated_code.lower()
    )
    details.append(
        CheckDetail(
            check_name="bounds_check_in_free",
            passed=has_bounds_check,
            expected="Pointer bounds validated before freeing to pool",
            actual="present" if has_bounds_check else "missing (invalid pointer not detected)",
            check_type="constraint",
        )
    )

    # Check: No cross-platform API contamination
    cross_plat = check_no_cross_platform_apis(generated_code, skip_platforms=["Linux_Userspace"])
    details.append(CheckDetail(
        check_name="no_cross_platform_apis",
        passed=len(cross_plat) == 0,
        expected="No FreeRTOS/Arduino/STM32_HAL/POSIX APIs",
        actual="clean" if not cross_plat else f"found: {[a for a, _ in cross_plat]}",
        check_type="constraint",
    ))

    return details
