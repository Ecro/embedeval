"""Behavioral checks for K_HEAP vs K_MEM_SLAB selection."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate heap and slab allocator behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: heap used for variable-size, slab for fixed-size (not swapped)
    # (LLM failure: using slab for variable-size allocation — impossible, wrong block size)
    has_heap_alloc = "k_heap_alloc" in generated_code
    has_slab_alloc = "k_mem_slab_alloc" in generated_code
    details.append(
        CheckDetail(
            check_name="both_allocators_used",
            passed=has_heap_alloc and has_slab_alloc,
            expected="Both k_heap_alloc and k_mem_slab_alloc called",
            actual=f"heap_alloc={has_heap_alloc}, slab_alloc={has_slab_alloc}",
            check_type="constraint",
        )
    )

    # Check 2: heap allocation checked for NULL
    # (LLM failure: k_heap_alloc returns NULL on failure, not error code)
    heap_alloc_pos = generated_code.find("k_heap_alloc")
    has_null_check = "!ptr" in generated_code or "== NULL" in generated_code or "!= NULL" in generated_code
    details.append(
        CheckDetail(
            check_name="heap_alloc_null_check",
            passed=has_null_check and heap_alloc_pos != -1,
            expected="NULL check after k_heap_alloc (returns NULL on failure)",
            actual="present" if has_null_check else "missing (silent alloc failure)",
            check_type="constraint",
        )
    )

    # Check 3: slab allocation checked for error code (not NULL)
    # (LLM failure: checking ptr==NULL instead of ret<0 for slab alloc)
    has_slab_err_check = "< 0" in generated_code or "!= 0" in generated_code
    details.append(
        CheckDetail(
            check_name="slab_alloc_error_check",
            passed=has_slab_err_check and has_slab_alloc,
            expected="Return value of k_mem_slab_alloc checked (returns int error code)",
            actual="present" if has_slab_err_check else "missing (use ret < 0, not NULL check)",
            check_type="constraint",
        )
    )

    # Check 4: heap_free matches heap_alloc
    # (LLM failure: allocates but never frees, or calls k_mem_slab_free on heap ptr)
    heap_alloc_count = generated_code.count("k_heap_alloc")
    heap_free_count = generated_code.count("k_heap_free")
    heap_balanced = heap_free_count >= heap_alloc_count and heap_alloc_count > 0
    details.append(
        CheckDetail(
            check_name="heap_alloc_free_balanced",
            passed=heap_balanced,
            expected="k_heap_free called for each k_heap_alloc",
            actual=f"heap_alloc={heap_alloc_count}, heap_free={heap_free_count}",
            check_type="constraint",
        )
    )

    # Check 5: slab_free matches slab_alloc
    slab_alloc_count = generated_code.count("k_mem_slab_alloc")
    slab_free_count = generated_code.count("k_mem_slab_free")
    slab_balanced = slab_free_count >= slab_alloc_count and slab_alloc_count > 0
    details.append(
        CheckDetail(
            check_name="slab_alloc_free_balanced",
            passed=slab_balanced,
            expected="k_mem_slab_free called for each k_mem_slab_alloc",
            actual=f"slab_alloc={slab_alloc_count}, slab_free={slab_free_count}",
            check_type="constraint",
        )
    )

    # Check 6: No raw malloc/calloc (heap-free outside of managed allocators)
    heap_funcs = ["malloc(", "calloc(", "k_malloc(", "k_calloc("]
    has_raw_heap = any(f in generated_code for f in heap_funcs)
    details.append(
        CheckDetail(
            check_name="no_raw_malloc",
            passed=not has_raw_heap,
            expected="No malloc/calloc (use k_heap_alloc or k_mem_slab_alloc)",
            actual="clean" if not has_raw_heap else "raw heap alloc found",
            check_type="constraint",
        )
    )

    # Check 7: no malloc/free cycle inside loops
    # (LLM failure: allocating and freeing inside a loop causes heap fragmentation over time)
    import re
    loop_regions = re.findall(
        r'(?:while|for)\s*\([^)]*\)\s*\{[^}]*(?:k_malloc|k_heap_alloc)[^}]*(?:k_free|k_heap_free)',
        generated_code,
        re.DOTALL,
    )
    has_alloc_in_loop = len(loop_regions) > 0
    details.append(CheckDetail(
        check_name="no_malloc_free_in_loop",
        passed=not has_alloc_in_loop,
        expected="No malloc/free cycle inside loops (causes fragmentation over time)",
        actual="clean" if not has_alloc_in_loop else "alloc/free in loop detected — fragmentation risk",
        check_type="constraint",
    ))

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
