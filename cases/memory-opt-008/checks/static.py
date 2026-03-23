"""Static analysis checks for Zephyr memory footprint Kconfig."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate memory footprint Kconfig options."""
    details: list[CheckDetail] = []

    has_fpu_off = "CONFIG_FPU=n" in generated_code
    details.append(
        CheckDetail(
            check_name="fpu_disabled",
            passed=has_fpu_off,
            expected="CONFIG_FPU=n (saves ~2-4KB)",
            actual="present" if has_fpu_off else "missing or FPU enabled",
            check_type="exact_match",
        )
    )

    has_minimal_libc = "CONFIG_MINIMAL_LIBC=y" in generated_code
    details.append(
        CheckDetail(
            check_name="minimal_libc_enabled",
            passed=has_minimal_libc,
            expected="CONFIG_MINIMAL_LIBC=y (saves ~20KB over newlib)",
            actual="present" if has_minimal_libc else "missing",
            check_type="exact_match",
        )
    )

    has_cbprintf_nano = "CONFIG_CBPRINTF_NANO=y" in generated_code
    details.append(
        CheckDetail(
            check_name="cbprintf_nano_enabled",
            passed=has_cbprintf_nano,
            expected="CONFIG_CBPRINTF_NANO=y (reduces printf size)",
            actual="present" if has_cbprintf_nano else "missing",
            check_type="exact_match",
        )
    )

    has_dynamic_thread_off = "CONFIG_DYNAMIC_THREAD=n" in generated_code
    details.append(
        CheckDetail(
            check_name="dynamic_thread_disabled",
            passed=has_dynamic_thread_off,
            expected="CONFIG_DYNAMIC_THREAD=n",
            actual="present" if has_dynamic_thread_off else "missing",
            check_type="exact_match",
        )
    )

    return details
