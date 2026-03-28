"""Behavioral checks for periodic control loop with deadline handling."""

import re

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate deadline miss detection in periodic control loop."""
    details: list[CheckDetail] = []

    # Check 1: Uses timing measurement API
    has_timing = any(api in generated_code for api in [
        "k_uptime_get", "k_cycle_get_32", "k_cycle_get",
        "k_uptime_ticks", "sys_clock_gettime",
    ])
    details.append(
        CheckDetail(
            check_name="timing_measurement_used",
            passed=has_timing,
            expected="Timing API used to measure iteration duration",
            actual="present" if has_timing else "MISSING (no timing measurement)",
            check_type="constraint",
        )
    )

    # Check 2: Deadline miss detection — compares elapsed vs period
    has_deadline_check = bool(re.search(
        r'(elapsed|duration|delta|diff|exec_time|dt)\s*[>>=]+\s*'
        r'(PERIOD|DEADLINE|period|deadline|K_MSEC|10|CONTROL)',
        generated_code,
    )) or bool(re.search(
        r'(deadline_miss|overrun_count|over_time|missed.*deadline'
        r'|deadline.*overrun)',
        generated_code, re.IGNORECASE,
    )) or bool(re.search(
        r'remaining\s*<=?\s*0',
        generated_code,
    )) or bool(re.search(
        r'if\s*\([^)]*remaining\s*>\s*0[^)]*\)\s*\{[^}]*\}\s*else\b',
        generated_code, re.DOTALL,
    ))
    details.append(
        CheckDetail(
            check_name="deadline_miss_detected",
            passed=has_deadline_check,
            expected="Deadline miss detection (elapsed > period comparison)",
            actual="present" if has_deadline_check
            else "MISSING (no deadline overrun detection)",
            check_type="constraint",
        )
    )

    # Check 3: Corrective action on deadline miss — requires an if-branch
    # that checks elapsed/duration/overrun, or a deadline miss counter
    has_corrective = bool(re.search(
        r'if\s*\([^)]*(?:elapsed|duration|delta|overrun|miss)[^)]*\)\s*\{',
        generated_code,
    )) or bool(re.search(
        r'(?:deadline_miss(?:es)?|overrun_count|miss_count)\s*[+][+]',
        generated_code,
    )) or bool(re.search(
        r'if\s*\([^)]*remaining\s*[<>]=?\s*0[^)]*\)\s*\{',
        generated_code,
    )) or bool(re.search(
        r'if\s*\([^)]*remaining\s*>\s*0[^)]*\)\s*\{[^}]*\}\s*else\s*\{',
        generated_code, re.DOTALL,
    ))
    details.append(
        CheckDetail(
            check_name="deadline_miss_action",
            passed=has_corrective,
            expected="Corrective action branch on deadline miss",
            actual="present" if has_corrective
            else "MISSING (no corrective action on overrun)",
            check_type="constraint",
        )
    )

    # Check 4: Period defined as constant (not magic number in sleep call)
    has_period_def = bool(re.search(
        r'#define\s+\w*(PERIOD|INTERVAL|CYCLE)\w*\s+',
        generated_code, re.IGNORECASE
    )) or bool(re.search(
        r'(?:const|static)\s+.*(?:period|interval)',
        generated_code, re.IGNORECASE
    ))
    details.append(
        CheckDetail(
            check_name="period_defined_as_constant",
            passed=has_period_def,
            expected="Period defined as named constant",
            actual="present" if has_period_def
            else "missing (period should not be magic number)",
            check_type="constraint",
        )
    )

    # Check 5: High priority thread (negative or <= 5 for Zephyr preemptive)
    # K_THREAD_DEFINE(name, stack_size, entry, p1, p2, p3, prio, options, delay)
    # Priority is argument 7 (index 6), so skip 6 comma-separated args first.
    priority_match = re.search(
        r'K_THREAD_DEFINE\s*\([^,]+,[^,]+,[^,]+,[^,]+,[^,]+,[^,]+,\s*([^,]+),',
        generated_code,
        re.DOTALL,
    )
    if not priority_match:
        # k_thread_create(tid, stack, stack_sz, entry, p1, p2, p3, prio, ...)
        # Priority is argument 8 (index 7).
        priority_match = re.search(
            r'k_thread_create\s*\([^,]+,[^,]+,[^,]+,[^,]+,[^,]+,[^,]+,[^,]+,\s*([^,]+),',
            generated_code,
            re.DOTALL,
        )

    has_high_prio = False
    if priority_match:
        prio_str = priority_match.group(1).strip()
        # Negative values or small positive = high priority
        try:
            prio_val = int(prio_str)
            has_high_prio = prio_val <= 5
        except ValueError:
            # It's a #define — resolve its numeric value and compare
            define_match = re.search(
                r'#define\s+' + re.escape(prio_str) + r'\s+(-?\d+)',
                generated_code,
            )
            if define_match:
                has_high_prio = int(define_match.group(1)) <= 5

    details.append(
        CheckDetail(
            check_name="high_priority_thread",
            passed=has_high_prio,
            expected="Control loop thread has high priority (<=5 or negative)",
            actual="high priority" if has_high_prio
            else "priority not verified as high",
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
