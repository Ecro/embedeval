"""Behavioral checks for Zephyr stack overflow detection."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate stack overflow detection behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: k_thread_stack_space_get API used (not custom canary)
    # (LLM hallucination: implementing custom stack probe instead of using Zephyr API)
    has_api = "k_thread_stack_space_get" in generated_code
    details.append(
        CheckDetail(
            check_name="zephyr_stack_api_used",
            passed=has_api,
            expected="k_thread_stack_space_get() used (correct Zephyr API)",
            actual="present" if has_api else "missing (use k_thread_stack_space_get, not custom probe)",
            check_type="constraint",
        )
    )

    # Check 2: Warning before overflow (proactive check, not post-crash)
    has_warn = (
        "LOG_WRN" in generated_code
        or "printk" in generated_code
        or "LOG_ERR" in generated_code
        or "pr_warn" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="warning_emitted_on_low_stack",
            passed=has_warn,
            expected="Warning logged when stack is low",
            actual="present" if has_warn else "missing (no warning on low stack)",
            check_type="constraint",
        )
    )

    # Check 3: Threshold comparison before emitting warning
    import re
    has_compare = bool(re.search(r'unused\s*[<>]=?\s*\w+|remaining\s*[<>]=?\s*\w+|space\s*[<>]=?\s*\w+', generated_code))
    has_threshold_kw = "threshold" in generated_code.lower() or "THRESHOLD" in generated_code
    details.append(
        CheckDetail(
            check_name="threshold_used_for_comparison",
            passed=has_compare or has_threshold_kw,
            expected="Stack remaining space compared against a threshold value",
            actual="present" if (has_compare or has_threshold_kw) else "missing",
            check_type="constraint",
        )
    )

    # Check 4: CONFIG_THREAD_STACK_INFO enabled (enables the API)
    has_config = "CONFIG_THREAD_STACK_INFO=y" in generated_code
    details.append(
        CheckDetail(
            check_name="config_enables_stack_info_api",
            passed=has_config,
            expected="CONFIG_THREAD_STACK_INFO=y enables k_thread_stack_space_get",
            actual="present" if has_config else "missing Kconfig option",
            check_type="constraint",
        )
    )

    # Check 5: k_current_get() used to get current thread handle
    has_current = "k_current_get" in generated_code
    details.append(
        CheckDetail(
            check_name="k_current_get_for_thread_handle",
            passed=has_current,
            expected="k_current_get() used to get current thread reference",
            actual="present" if has_current else "missing",
            check_type="constraint",
        )
    )

    return details
