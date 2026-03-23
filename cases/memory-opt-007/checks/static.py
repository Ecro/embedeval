"""Static analysis checks for object pool pattern."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate object pool code structure."""
    details: list[CheckDetail] = []

    has_static_array = "static" in generated_code and "pool[" in generated_code.lower() or (
        "static" in generated_code and "[" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="static_pool_array_defined",
            passed=has_static_array,
            expected="Static pool array defined (not heap-allocated)",
            actual="present" if has_static_array else "missing",
            check_type="exact_match",
        )
    )

    has_alloc_fn = "pool_alloc" in generated_code or "_alloc(" in generated_code
    details.append(
        CheckDetail(
            check_name="alloc_function_defined",
            passed=has_alloc_fn,
            expected="Pool alloc function defined",
            actual="present" if has_alloc_fn else "missing",
            check_type="exact_match",
        )
    )

    has_free_fn = "pool_free" in generated_code or "_free(" in generated_code
    details.append(
        CheckDetail(
            check_name="free_function_defined",
            passed=has_free_fn,
            expected="Pool free function defined",
            actual="present" if has_free_fn else "missing",
            check_type="exact_match",
        )
    )

    heap_funcs = ["malloc(", "calloc(", "k_malloc(", "k_calloc("]
    has_heap = any(f in generated_code for f in heap_funcs)
    details.append(
        CheckDetail(
            check_name="no_heap_allocation",
            passed=not has_heap,
            expected="No malloc/calloc/k_malloc (heap-free pool)",
            actual="heap-free" if not has_heap else "VIOLATION: heap allocation found in pool",
            check_type="exact_match",
        )
    )

    has_null_return = "return NULL" in generated_code
    details.append(
        CheckDetail(
            check_name="null_returned_on_exhaustion",
            passed=has_null_return,
            expected="NULL returned when pool is exhausted",
            actual="present" if has_null_return else "missing",
            check_type="exact_match",
        )
    )

    return details
