"""Behavioral checks for Zephyr memory footprint Kconfig."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate memory footprint Kconfig behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: CONFIG_FPU=n (not =y which would increase footprint)
    has_fpu_n = "CONFIG_FPU=n" in generated_code
    has_fpu_y = "CONFIG_FPU=y" in generated_code
    details.append(
        CheckDetail(
            check_name="fpu_correctly_disabled",
            passed=has_fpu_n and not has_fpu_y,
            expected="CONFIG_FPU=n (disabled, not enabled)",
            actual="correct" if (has_fpu_n and not has_fpu_y) else "WRONG: FPU enabled or missing",
            check_type="constraint",
        )
    )

    # Check 2: No conflicting enables (NEWLIB and MINIMAL_LIBC conflict)
    has_newlib = "CONFIG_NEWLIB_LIBC=y" in generated_code
    has_minimal = "CONFIG_MINIMAL_LIBC=y" in generated_code
    details.append(
        CheckDetail(
            check_name="no_conflicting_libc",
            passed=not (has_newlib and has_minimal),
            expected="No conflicting NEWLIB_LIBC=y and MINIMAL_LIBC=y",
            actual="no conflict" if not (has_newlib and has_minimal) else "CONFLICT: both newlib and minimal libc enabled",
            check_type="constraint",
        )
    )

    # Check 3: All size-reducing options present
    size_reducers = [
        "CONFIG_MINIMAL_LIBC=y",
        "CONFIG_CBPRINTF_NANO=y",
        "CONFIG_FPU=n",
        "CONFIG_DYNAMIC_THREAD=n",
    ]
    found_count = sum(1 for opt in size_reducers if opt in generated_code)
    details.append(
        CheckDetail(
            check_name="multiple_size_reducing_options",
            passed=found_count >= 3,
            expected="At least 3 of 4 core size-reducing options set",
            actual=f"{found_count}/4 core options present",
            check_type="constraint",
        )
    )

    # Check 4: No CONFIG_DEBUG=y (size-increasing)
    has_debug = "CONFIG_DEBUG=y" in generated_code
    details.append(
        CheckDetail(
            check_name="no_debug_enabled",
            passed=not has_debug,
            expected="CONFIG_DEBUG not enabled (increases size)",
            actual="clean" if not has_debug else "WRONG: CONFIG_DEBUG=y increases footprint",
            check_type="constraint",
        )
    )

    # Check 5: MAIN_STACK_SIZE set to small value (not default 2048)
    import re
    stack_match = re.search(r'CONFIG_MAIN_STACK_SIZE=(\d+)', generated_code)
    stack_size = int(stack_match.group(1)) if stack_match else None
    stack_ok = stack_size is not None and stack_size <= 1024
    details.append(
        CheckDetail(
            check_name="main_stack_size_minimized",
            passed=stack_ok,
            expected="CONFIG_MAIN_STACK_SIZE <= 1024 (minimized)",
            actual=f"{stack_size}" if stack_size else "not set",
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
