"""Behavioral checks for Zephyr thread stack analyzer."""

import re

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate thread analyzer behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: thread_analyzer_print called (not thread_analyze or other wrong API)
    # (LLM failure: calling wrong function like thread_analyze() or stack_analyzer_print())
    has_correct_api = "thread_analyzer_print" in generated_code
    has_wrong_api = (
        "thread_analyze(" in generated_code
        or "stack_analyzer_print" in generated_code
        or "thread_stack_dump" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="correct_analyzer_api",
            passed=has_correct_api and not has_wrong_api,
            expected="thread_analyzer_print() called (correct Zephyr API)",
            actual="correct" if (has_correct_api and not has_wrong_api) else "wrong API name",
            check_type="constraint",
        )
    )

    # Check 2: k_sleep called BEFORE thread_analyzer_print (threads must run first)
    # (LLM failure: calling thread_analyzer_print immediately at boot = all zeros)
    sleep_pos = generated_code.find("k_sleep")
    analyzer_pos = generated_code.find("thread_analyzer_print")
    called_after_sleep = (
        sleep_pos != -1 and analyzer_pos != -1 and sleep_pos < analyzer_pos
    )
    details.append(
        CheckDetail(
            check_name="analyzer_called_after_sleep",
            passed=called_after_sleep,
            expected="k_sleep() before thread_analyzer_print() (threads need time to run)",
            actual="correct order" if called_after_sleep else "wrong order (all-zero results!)",
            check_type="constraint",
        )
    )

    # Check 3: k_thread_create called (secondary thread exists to analyze)
    has_thread_create = "k_thread_create" in generated_code
    details.append(
        CheckDetail(
            check_name="secondary_thread_created",
            passed=has_thread_create,
            expected="k_thread_create() called to create a thread to analyze",
            actual="present" if has_thread_create else "missing (only main thread)",
            check_type="constraint",
        )
    )

    # Check 4: CONFIG_THREAD_ANALYZER referenced (in comment or prj.conf)
    has_config = "CONFIG_THREAD_ANALYZER" in generated_code
    details.append(
        CheckDetail(
            check_name="config_thread_analyzer_referenced",
            passed=has_config,
            expected="CONFIG_THREAD_ANALYZER referenced (must be enabled in prj.conf)",
            actual="present" if has_config else "MISSING (analyzer not enabled at compile!)",
            check_type="constraint",
        )
    )

    # Check 5: K_THREAD_STACK_DEFINE used for thread stack
    has_stack_define = "K_THREAD_STACK_DEFINE" in generated_code
    details.append(
        CheckDetail(
            check_name="thread_stack_define_used",
            passed=has_stack_define,
            expected="K_THREAD_STACK_DEFINE for proper Zephyr thread stack alignment",
            actual="present" if has_stack_define else "missing (raw array won't work)",
            check_type="constraint",
        )
    )

    # Check 6: CONFIG_THREAD_ANALYZER_USE_PRINTK referenced
    # (LLM failure: enabling analyzer but not printk backend = silent output)
    has_printk_config = "CONFIG_THREAD_ANALYZER_USE_PRINTK" in generated_code
    details.append(
        CheckDetail(
            check_name="thread_analyzer_printk_backend",
            passed=has_printk_config,
            expected="CONFIG_THREAD_ANALYZER_USE_PRINTK referenced for visible output",
            actual="present" if has_printk_config else "missing (analyzer output may be silent)",
            check_type="constraint",
        )
    )

    # Check 7: Stack size must not be excessive (> 4096 bytes is wasteful on embedded)
    # LLM failure: using large desktop-sized stacks when SRAM is precious
    stack_define_match = re.search(
        r"K_THREAD_STACK_DEFINE\s*\(\s*\w+\s*,\s*(\w+)\s*\)",
        generated_code,
    )
    stack_size_ok = True
    stack_size_actual = "not found"
    if stack_define_match:
        size_token = stack_define_match.group(1)
        # Try to resolve as a literal integer first
        if size_token.isdigit():
            stack_size = int(size_token)
        else:
            # Try to resolve via #define
            define_match = re.search(
                rf"#define\s+{re.escape(size_token)}\s+(\d+)",
                generated_code,
            )
            stack_size = int(define_match.group(1)) if define_match else None
        if stack_size is not None:
            stack_size_ok = stack_size <= 4096
            stack_size_actual = f"{stack_size} bytes"
        else:
            stack_size_actual = f"macro {size_token} (unresolved)"
    details.append(
        CheckDetail(
            check_name="stack_size_not_excessive",
            passed=stack_size_ok,
            expected="Thread stack size <= 4096 bytes (embedded SRAM is scarce)",
            actual=stack_size_actual if stack_size_ok else f"{stack_size_actual} - EXCESSIVE",
            check_type="constraint",
        )
    )

    # Check 8: k_malloc without heap config is a common LLM error
    # On embedded, malloc silently fails unless K_HEAP_DEFINE or CONFIG_HEAP_MEM_POOL_SIZE present
    has_malloc = bool(re.search(r"\bk_malloc\b|\bmalloc\b", generated_code))
    if not has_malloc:
        # No malloc at all — trivially pass
        heap_config_ok = True
        heap_actual = "no malloc used"
    else:
        has_heap_define = "K_HEAP_DEFINE" in generated_code
        has_heap_config = "CONFIG_HEAP_MEM_POOL_SIZE" in generated_code
        heap_config_ok = has_heap_define or has_heap_config
        heap_actual = (
            "K_HEAP_DEFINE or CONFIG_HEAP_MEM_POOL_SIZE present"
            if heap_config_ok
            else "malloc without heap config - will fail on target"
        )
    details.append(
        CheckDetail(
            check_name="no_heap_allocation_without_pool",
            passed=heap_config_ok,
            expected="If malloc/k_malloc used, K_HEAP_DEFINE or CONFIG_HEAP_MEM_POOL_SIZE must be present",
            actual=heap_actual,
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
