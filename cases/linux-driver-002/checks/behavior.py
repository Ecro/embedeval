"""Behavioral checks for Linux platform driver with Device Tree binding."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate platform driver behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: of_match_table wired into driver.of_match_table
    # (LLM failure: defines of_device_id table but forgets to assign it)
    has_of_match_table = ".of_match_table" in generated_code
    details.append(
        CheckDetail(
            check_name="of_match_table_assigned",
            passed=has_of_match_table,
            expected=".of_match_table assigned in platform_driver.driver",
            actual="present" if has_of_match_table else "MISSING (DT won't match!)",
            check_type="constraint",
        )
    )

    # Check 2: MODULE_DEVICE_TABLE(of, ...) present
    # (LLM failure: omits MODULE_DEVICE_TABLE so modprobe cannot auto-load)
    has_module_device_table = "MODULE_DEVICE_TABLE(of" in generated_code
    details.append(
        CheckDetail(
            check_name="module_device_table_of",
            passed=has_module_device_table,
            expected="MODULE_DEVICE_TABLE(of, ...) for auto-load support",
            actual="present" if has_module_device_table else "MISSING (no auto-load!)",
            check_type="constraint",
        )
    )

    # Check 3: probe returns 0 on success (not void, not negative)
    # (LLM failure: probe returning void or wrong error code)
    has_probe_return = "return 0" in generated_code
    details.append(
        CheckDetail(
            check_name="probe_returns_zero",
            passed=has_probe_return,
            expected="probe function returns 0 on success",
            actual="present" if has_probe_return else "missing",
            check_type="constraint",
        )
    )

    # Check 4: sentinel entry in of_device_id table
    # (LLM failure: no {} terminator causes kernel oops walking the table)
    code_stripped = generated_code.replace(" ", "").replace("\t", "")
    has_sentinel = "{}" in code_stripped or "{}," in code_stripped
    details.append(
        CheckDetail(
            check_name="of_match_table_sentinel",
            passed=has_sentinel,
            expected="of_device_id table ends with {} sentinel",
            actual="present" if has_sentinel else "MISSING (kernel oops!)",
            check_type="constraint",
        )
    )

    # Check 5: module_platform_driver() or explicit register/unregister
    # (LLM failure: no registration call at all)
    has_register = (
        "module_platform_driver" in generated_code
        or "platform_driver_register" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="driver_registered",
            passed=has_register,
            expected="module_platform_driver() or platform_driver_register() called",
            actual="present" if has_register else "MISSING (driver never loads!)",
            check_type="constraint",
        )
    )

    # Check 6: probe function has correct first argument type
    has_platform_device_arg = "struct platform_device" in generated_code
    details.append(
        CheckDetail(
            check_name="probe_platform_device_arg",
            passed=has_platform_device_arg,
            expected="probe takes struct platform_device * argument",
            actual="present" if has_platform_device_arg else "missing",
            check_type="exact_match",
        )
    )

    return details
