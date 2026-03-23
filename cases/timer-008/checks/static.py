"""Static analysis checks for high-resolution cycle-count timing application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate cycle-count timing code structure and required elements."""
    details: list[CheckDetail] = []

    # Check 1: Includes zephyr/kernel.h
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

    # Check 2: Uses k_cycle_get_32 (Zephyr cycle counter)
    has_cycle_get = "k_cycle_get_32" in generated_code
    details.append(
        CheckDetail(
            check_name="uses_k_cycle_get_32",
            passed=has_cycle_get,
            expected="k_cycle_get_32() used for cycle counting",
            actual="present" if has_cycle_get else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: Uses k_cyc_to_ns_floor64 for conversion
    has_ns_convert = "k_cyc_to_ns_floor64" in generated_code
    details.append(
        CheckDetail(
            check_name="uses_k_cyc_to_ns_floor64",
            passed=has_ns_convert,
            expected="k_cyc_to_ns_floor64() used for cycle-to-ns conversion",
            actual="present" if has_ns_convert else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Hallucination — no clock_gettime (Linux POSIX)
    has_clock_gettime = "clock_gettime" in generated_code
    details.append(
        CheckDetail(
            check_name="no_clock_gettime_hallucination",
            passed=not has_clock_gettime,
            expected="clock_gettime() not used (Linux POSIX API, wrong platform)",
            actual="POSIX API found" if has_clock_gettime else "clean",
            check_type="constraint",
        )
    )

    # Check 5: Hallucination — no Arduino micros()
    has_arduino_micros = "micros()" in generated_code
    details.append(
        CheckDetail(
            check_name="no_arduino_micros_hallucination",
            passed=not has_arduino_micros,
            expected="micros() not used (Arduino API, wrong platform)",
            actual="Arduino API found" if has_arduino_micros else "clean",
            check_type="constraint",
        )
    )

    # Check 6: Hallucination — no STM32 HAL_GetTick
    has_hal_tick = "HAL_GetTick" in generated_code
    details.append(
        CheckDetail(
            check_name="no_hal_gettick_hallucination",
            passed=not has_hal_tick,
            expected="HAL_GetTick() not used (STM32 HAL, wrong platform)",
            actual="STM32 HAL found" if has_hal_tick else "clean",
            check_type="constraint",
        )
    )

    # Check 7: Uses uint64_t for nanosecond result (avoids overflow)
    has_u64 = "uint64_t" in generated_code
    details.append(
        CheckDetail(
            check_name="uses_uint64_for_nanoseconds",
            passed=has_u64,
            expected="uint64_t used for nanosecond value (avoids 32-bit overflow)",
            actual="present" if has_u64 else "missing",
            check_type="constraint",
        )
    )

    return details
