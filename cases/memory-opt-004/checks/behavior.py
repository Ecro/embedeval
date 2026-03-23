"""Behavioral checks for Zephyr thread stack analyzer."""

from embedeval.models import CheckDetail


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

    return details
