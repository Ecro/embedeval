"""Behavioral checks for memory slab allocation."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis, has_error_check


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate memory slab behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: alloc before free (correct lifecycle)
    alloc_pos = generated_code.find("k_mem_slab_alloc")
    free_pos = generated_code.find("k_mem_slab_free")
    order_ok = alloc_pos != -1 and free_pos != -1 and alloc_pos < free_pos
    details.append(
        CheckDetail(
            check_name="alloc_before_free",
            passed=order_ok,
            expected="k_mem_slab_alloc before k_mem_slab_free",
            actual="correct order" if order_ok else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: Error handling for alloc failure
    # (LLM failure: not checking if alloc returns NULL/error)
    has_alloc_check = has_error_check(generated_code)
    details.append(
        CheckDetail(
            check_name="alloc_error_check",
            passed=has_alloc_check,
            expected="Return value checked after k_mem_slab_alloc",
            actual="present" if has_alloc_check else "missing",
            check_type="constraint",
        )
    )

    # Check 3: Free called for every alloc path
    # (LLM failure: memory leak on error paths)
    alloc_count = generated_code.count("k_mem_slab_alloc")
    free_count = generated_code.count("k_mem_slab_free")
    balanced = free_count >= alloc_count and alloc_count > 0
    details.append(
        CheckDetail(
            check_name="balanced_alloc_free",
            passed=balanced,
            expected="At least as many frees as allocs",
            actual=f"alloc={alloc_count}, free={free_count}",
            check_type="constraint",
        )
    )

    # Check 4: No heap usage (reinforced behavioral check)
    heap_funcs = ["malloc(", "calloc(", "k_malloc(", "realloc("]
    has_heap = any(f in generated_code for f in heap_funcs)
    details.append(
        CheckDetail(
            check_name="no_heap_behavioral",
            passed=not has_heap,
            expected="Zero heap allocations in entire program",
            actual="heap found" if has_heap else "clean",
            check_type="constraint",
        )
    )

    # Check 5: Block size and count are positive constants
    has_block_size = "BLOCK_SIZE" in generated_code or "block_size" in generated_code
    details.append(
        CheckDetail(
            check_name="block_size_defined",
            passed=has_block_size,
            expected="Block size defined as named constant",
            actual="present" if has_block_size else "missing",
            check_type="exact_match",
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
