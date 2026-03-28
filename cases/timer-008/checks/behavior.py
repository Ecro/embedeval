"""Behavioral checks for high-resolution cycle-count timing application."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate cycle-count timing behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: k_cycle_get_32 called at least twice (start and end)
    cycle_count = generated_code.count("k_cycle_get_32")
    two_reads = cycle_count >= 2
    details.append(
        CheckDetail(
            check_name="cycle_get_called_twice",
            passed=two_reads,
            expected="k_cycle_get_32() called at least twice (start and end)",
            actual=f"k_cycle_get_32 called {cycle_count} time(s)",
            check_type="constraint",
        )
    )

    # Check 2: Elapsed cycles computed as end - start
    has_subtraction = "end - start" in generated_code or "elapsed" in generated_code.lower()
    details.append(
        CheckDetail(
            check_name="elapsed_cycles_computed",
            passed=has_subtraction,
            expected="Elapsed cycles computed (end - start or elapsed variable)",
            actual="present" if has_subtraction else "missing",
            check_type="constraint",
        )
    )

    # Check 3: Conversion from cycles to nanoseconds present
    ns_pos = generated_code.find("k_cyc_to_ns_floor64")
    cycle_pos = generated_code.find("k_cycle_get_32")
    order_ok = cycle_pos != -1 and ns_pos != -1 and cycle_pos < ns_pos
    details.append(
        CheckDetail(
            check_name="ns_conversion_after_measurement",
            passed=order_ok,
            expected="k_cyc_to_ns_floor64 called after k_cycle_get_32",
            actual="correct order" if order_ok else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 4: Bounded loop (not infinite — 10 iterations)
    import re
    has_bounded_loop = bool(re.search(r"for\s*\(\s*int\s+\w+\s*=\s*0\s*;\s*\w+\s*<\s*\d+", generated_code))
    details.append(
        CheckDetail(
            check_name="bounded_loop",
            passed=has_bounded_loop,
            expected="Bounded for loop used (not infinite while loop)",
            actual="present" if has_bounded_loop else "missing",
            check_type="constraint",
        )
    )

    # Check 5: Sleep between measurements (not tight loop)
    has_sleep = "k_sleep" in generated_code
    details.append(
        CheckDetail(
            check_name="sleep_between_measurements",
            passed=has_sleep,
            expected="k_sleep() used between measurements",
            actual="present" if has_sleep else "missing",
            check_type="constraint",
        )
    )

    # Check 6: No gettimeofday (POSIX/Linux)
    has_gettimeofday = "gettimeofday" in generated_code
    details.append(
        CheckDetail(
            check_name="no_gettimeofday",
            passed=not has_gettimeofday,
            expected="gettimeofday() not used (POSIX API, wrong platform)",
            actual="POSIX API found" if has_gettimeofday else "clean",
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
