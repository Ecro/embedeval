"""Static analysis checks for peripheral power gating."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate peripheral power gating API correctness — no hallucinated APIs."""
    details: list[CheckDetail] = []

    # Check 1: PM device header
    has_pm_h = "zephyr/pm/device.h" in generated_code
    details.append(
        CheckDetail(
            check_name="pm_device_header",
            passed=has_pm_h,
            expected="zephyr/pm/device.h included",
            actual="present" if has_pm_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: pm_device_action_run used (correct Zephyr API)
    has_action_run = "pm_device_action_run" in generated_code
    details.append(
        CheckDetail(
            check_name="pm_device_action_run_used",
            passed=has_action_run,
            expected="pm_device_action_run() used for PM transitions",
            actual="present" if has_action_run else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: PM_DEVICE_ACTION_SUSPEND used (gate peripheral)
    has_suspend = "PM_DEVICE_ACTION_SUSPEND" in generated_code
    details.append(
        CheckDetail(
            check_name="suspend_action_used",
            passed=has_suspend,
            expected="PM_DEVICE_ACTION_SUSPEND used to gate peripheral",
            actual="present" if has_suspend else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: PM_DEVICE_ACTION_RESUME used (enable peripheral before use)
    has_resume = "PM_DEVICE_ACTION_RESUME" in generated_code
    details.append(
        CheckDetail(
            check_name="resume_action_used",
            passed=has_resume,
            expected="PM_DEVICE_ACTION_RESUME used before accessing peripheral",
            actual="present" if has_resume else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: No hallucinated APIs
    hallucinated_apis = [
        "peripheral_power_off",
        "peripheral_power_on",
        "clk_disable",
        "clk_enable",
    ]
    found_hallucinated = [api for api in hallucinated_apis if api in generated_code]
    details.append(
        CheckDetail(
            check_name="no_hallucinated_apis",
            passed=len(found_hallucinated) == 0,
            expected="No non-existent Zephyr APIs (peripheral_power_off, clk_disable, etc.)",
            actual=f"hallucinated: {found_hallucinated}" if found_hallucinated else "clean",
            check_type="constraint",
        )
    )

    # Check 6: State tracking present
    has_state = (
        "peripheral_active" in generated_code
        or "active" in generated_code
        or "suspended" in generated_code
        or "state" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="state_tracking_present",
            passed=has_state,
            expected="Peripheral state tracked before PM transitions",
            actual="present" if has_state else "missing",
            check_type="constraint",
        )
    )

    return details
