"""Static analysis checks for ISR-safe FIFO with k_fifo."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate ISR-safe k_fifo usage constraints."""
    details: list[CheckDetail] = []

    # Check 1: kernel header included
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

    # Check 2: k_fifo used (not FreeRTOS xQueue)
    has_kfifo = "k_fifo" in generated_code
    details.append(
        CheckDetail(
            check_name="uses_k_fifo",
            passed=has_kfifo,
            expected="k_fifo used (not FreeRTOS xQueueSendFromISR)",
            actual="present" if has_kfifo else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: No FreeRTOS APIs
    freertos_apis = ["xQueueSendFromISR", "xQueueReceive", "xQueueCreate", "QueueHandle_t"]
    has_freertos = any(api in generated_code for api in freertos_apis)
    details.append(
        CheckDetail(
            check_name="no_freertos_apis",
            passed=not has_freertos,
            expected="No FreeRTOS queue APIs (xQueueSendFromISR etc.)",
            actual="FreeRTOS API found" if has_freertos else "clean",
            check_type="constraint",
        )
    )

    # Check 4: k_fifo_put present (ISR side)
    has_put = "k_fifo_put" in generated_code
    details.append(
        CheckDetail(
            check_name="k_fifo_put_present",
            passed=has_put,
            expected="k_fifo_put() called (ISR-safe enqueue)",
            actual="present" if has_put else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: k_fifo_get present (thread side)
    has_get = "k_fifo_get" in generated_code
    details.append(
        CheckDetail(
            check_name="k_fifo_get_present",
            passed=has_get,
            expected="k_fifo_get() called (thread-side dequeue)",
            actual="present" if has_get else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: No k_malloc calls (forbidden in ISR; ignore mentions in comments)
    import re
    # Strip single-line and block comments before checking
    code_no_comments = re.sub(r'/\*.*?\*/', '', generated_code, flags=re.DOTALL)
    code_no_comments = re.sub(r'//[^\n]*', '', code_no_comments)
    has_kmalloc = bool(re.search(r'\bk_malloc\s*\(', code_no_comments))
    details.append(
        CheckDetail(
            check_name="no_k_malloc",
            passed=not has_kmalloc,
            expected="No k_malloc (forbidden in ISR; use static pool)",
            actual="k_malloc found" if has_kmalloc else "clean",
            check_type="constraint",
        )
    )

    # Check 7: fifo_reserved field present (required by k_fifo linked list)
    has_reserved = "fifo_reserved" in generated_code
    details.append(
        CheckDetail(
            check_name="fifo_reserved_field",
            passed=has_reserved,
            expected="fifo_reserved field as first struct member",
            actual="present" if has_reserved else "missing (k_fifo requires this)",
            check_type="exact_match",
        )
    )

    return details
