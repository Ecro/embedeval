"""Behavioral checks for real-time thread with deadline measurement."""

import re

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate deadline measurement behavioral correctness."""
    details: list[CheckDetail] = []

    # Check 1: k_cycle_get_32 called twice (start and end timestamps)
    cycle_count = generated_code.count("k_cycle_get_32")
    details.append(
        CheckDetail(
            check_name="two_timestamps_taken",
            passed=cycle_count >= 2,
            expected="k_cycle_get_32() called at least twice (t0 and t1)",
            actual=f"k_cycle_get_32 count={cycle_count}",
            check_type="constraint",
        )
    )

    # Check 2: Elapsed time computed (t1 - t0 pattern)
    has_elapsed = bool(
        re.search(r"\bt1\s*-\s*t0\b|\bend\s*-\s*start\b|\bstop\s*-\s*start\b", generated_code)
    )
    details.append(
        CheckDetail(
            check_name="elapsed_time_computed",
            passed=has_elapsed,
            expected="Elapsed cycles computed as (t1 - t0)",
            actual="elapsed computation found" if has_elapsed else "no elapsed computation",
            check_type="constraint",
        )
    )

    # Check 3: No k_sleep in the timed work section
    # LLM failure: calling k_sleep inside the deadline measurement window
    # Find the RT thread function body
    rt_fn_match = re.search(
        r"void\s+\w*(?:rt|real_time|deadline|timed)\w*\s*\([^)]*\)\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}",
        generated_code,
        re.IGNORECASE | re.DOTALL,
    )
    sleep_in_critical_path = False
    if rt_fn_match:
        fn_body = rt_fn_match.group(1)
        # Look for k_sleep between the two k_cycle_get_32 calls
        between_timestamps = re.search(
            r"k_cycle_get_32.*?k_sleep.*?k_cycle_get_32",
            fn_body,
            re.DOTALL,
        )
        sleep_in_critical_path = between_timestamps is not None
    details.append(
        CheckDetail(
            check_name="no_sleep_in_timed_section",
            passed=not sleep_in_critical_path,
            expected="No k_sleep between timing start and end",
            actual="k_sleep in critical path (BUG)" if sleep_in_critical_path else "clean",
            check_type="constraint",
        )
    )

    # Check 4: Deadline miss printed
    has_deadline_msg = "DEADLINE" in generated_code or "deadline" in generated_code.lower()
    details.append(
        CheckDetail(
            check_name="deadline_miss_reported",
            passed=has_deadline_msg,
            expected="Deadline miss case reported with printk",
            actual="present" if has_deadline_msg else "missing",
            check_type="constraint",
        )
    )

    # Check 5: Thread loops (periodic deadline check)
    has_loop = bool(re.search(r"while\s*\(\s*(?:1|true)\s*\)", generated_code))
    details.append(
        CheckDetail(
            check_name="thread_is_periodic",
            passed=has_loop,
            expected="Thread loops (periodic deadline measurement)",
            actual="loop found" if has_loop else "single-shot only",
            check_type="constraint",
        )
    )

    # Check 6: Deadline/timeout value is a named constant, not a magic number
    # LLM failure: hardcoding numbers like `if (elapsed > 10000)` instead of
    # `#define DEADLINE_US 10000` or `const uint32_t deadline = 10000`
    has_named_deadline_const = bool(
        re.search(
            r"#define\s+\w*(?:DEADLINE|TIMEOUT|PERIOD|LIMIT)\w*\s+\d+",
            generated_code,
            re.IGNORECASE,
        )
        or re.search(
            r"const\s+\w+\s+\w*(?:deadline|timeout)\w*\s*=",
            generated_code,
            re.IGNORECASE,
        )
    )
    details.append(
        CheckDetail(
            check_name="deadline_constant_not_magic",
            passed=has_named_deadline_const,
            expected="Deadline/timeout value as named constant (#define or const variable)",
            actual="named constant found" if has_named_deadline_const else "magic number - anti-pattern",
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
