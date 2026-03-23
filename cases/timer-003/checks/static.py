"""Static analysis checks for hardware counter with alarm application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate counter alarm code structure and required elements."""
    details: list[CheckDetail] = []

    # Check 1: Includes counter header
    has_counter_h = "zephyr/drivers/counter.h" in generated_code
    details.append(
        CheckDetail(
            check_name="counter_header_included",
            passed=has_counter_h,
            expected="zephyr/drivers/counter.h included",
            actual="present" if has_counter_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: Includes kernel header
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

    # Check 3: Uses counter_start
    has_start = "counter_start" in generated_code
    details.append(
        CheckDetail(
            check_name="counter_started",
            passed=has_start,
            expected="counter_start() called",
            actual="present" if has_start else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Uses counter_set_channel_alarm
    has_alarm = "counter_set_channel_alarm" in generated_code
    details.append(
        CheckDetail(
            check_name="channel_alarm_set",
            passed=has_alarm,
            expected="counter_set_channel_alarm() called",
            actual="present" if has_alarm else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Has an alarm callback function defined
    has_callback = ".callback" in generated_code or "alarm_callback" in generated_code
    details.append(
        CheckDetail(
            check_name="alarm_callback_defined",
            passed=has_callback,
            expected="Alarm callback function defined and assigned",
            actual="present" if has_callback else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: Uses device_is_ready check (AI failure: missing readiness check)
    has_ready = "device_is_ready" in generated_code
    details.append(
        CheckDetail(
            check_name="device_ready_check",
            passed=has_ready,
            expected="device_is_ready() check before counter operations",
            actual="present" if has_ready else "missing",
            check_type="constraint",
        )
    )

    return details
