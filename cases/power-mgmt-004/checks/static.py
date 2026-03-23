"""Static analysis checks for PM device runtime enable/disable."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate PM runtime code structure and required elements."""
    details: list[CheckDetail] = []

    # Check 1: PM device runtime header
    has_runtime_h = "zephyr/pm/device_runtime.h" in generated_code
    details.append(
        CheckDetail(
            check_name="pm_device_runtime_header",
            passed=has_runtime_h,
            expected="zephyr/pm/device_runtime.h included",
            actual="present" if has_runtime_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: pm_device_runtime_enable called
    has_enable = "pm_device_runtime_enable" in generated_code
    details.append(
        CheckDetail(
            check_name="runtime_enable_called",
            passed=has_enable,
            expected="pm_device_runtime_enable() called",
            actual="present" if has_enable else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: pm_device_runtime_get called
    has_get = "pm_device_runtime_get" in generated_code
    details.append(
        CheckDetail(
            check_name="runtime_get_called",
            passed=has_get,
            expected="pm_device_runtime_get() called",
            actual="present" if has_get else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: pm_device_runtime_put called
    has_put = "pm_device_runtime_put" in generated_code
    details.append(
        CheckDetail(
            check_name="runtime_put_called",
            passed=has_put,
            expected="pm_device_runtime_put() called",
            actual="present" if has_put else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: pm_device_runtime_disable called
    has_disable = "pm_device_runtime_disable" in generated_code
    details.append(
        CheckDetail(
            check_name="runtime_disable_called",
            passed=has_disable,
            expected="pm_device_runtime_disable() called",
            actual="present" if has_disable else "missing",
            check_type="exact_match",
        )
    )

    return details
