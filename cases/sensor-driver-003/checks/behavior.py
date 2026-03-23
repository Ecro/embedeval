"""Behavioral checks for multi-channel accelerometer read."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate multi-channel sensor read behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: sensor_sample_fetch called only once per iteration
    # (LLM failure: calling fetch 3 times, once per channel)
    # Count actual call sites: lines containing sensor_sample_fetch( but NOT inside a string literal
    fetch_call_lines = [
        line for line in generated_code.splitlines()
        if "sensor_sample_fetch(" in line and not line.strip().startswith('"') and "printk" not in line
    ]
    fetch_call_count = len(fetch_call_lines)
    details.append(
        CheckDetail(
            check_name="single_fetch_per_cycle",
            passed=fetch_call_count == 1,
            expected="sensor_sample_fetch() called exactly once per loop iteration (1 call site)",
            actual=f"found {fetch_call_count} call site(s): {fetch_call_lines}",
            check_type="constraint",
        )
    )

    # Check 2: All three channels read from single fetch snapshot
    all_channels = all(
        ch in generated_code
        for ch in ["SENSOR_CHAN_ACCEL_X", "SENSOR_CHAN_ACCEL_Y", "SENSOR_CHAN_ACCEL_Z"]
    )
    details.append(
        CheckDetail(
            check_name="all_three_channels_read",
            passed=all_channels,
            expected="SENSOR_CHAN_ACCEL_X, Y, and Z all read",
            actual="all present" if all_channels else "missing one or more channels",
            check_type="constraint",
        )
    )

    # Check 3: fetch before any channel_get (correct ordering)
    fetch_pos = generated_code.find("sensor_sample_fetch")
    get_x_pos = generated_code.find("SENSOR_CHAN_ACCEL_X")
    details.append(
        CheckDetail(
            check_name="fetch_before_channel_get",
            passed=fetch_pos != -1 and get_x_pos != -1 and fetch_pos < get_x_pos,
            expected="sensor_sample_fetch() before sensor_channel_get()",
            actual="correct" if (fetch_pos != -1 and get_x_pos != -1 and fetch_pos < get_x_pos) else "wrong order",
            check_type="constraint",
        )
    )

    # Check 4: device_is_ready check present
    has_ready = "device_is_ready" in generated_code
    details.append(
        CheckDetail(
            check_name="device_ready_check",
            passed=has_ready,
            expected="device_is_ready() called before sensor operations",
            actual="present" if has_ready else "missing",
            check_type="constraint",
        )
    )

    # Check 5: Periodic loop with sleep
    has_loop = "while" in generated_code
    has_sleep = "k_sleep" in generated_code
    details.append(
        CheckDetail(
            check_name="periodic_loop",
            passed=has_loop and has_sleep,
            expected="Periodic read loop with k_sleep()",
            actual=f"loop={has_loop}, sleep={has_sleep}",
            check_type="constraint",
        )
    )

    # Check 6: Error handling present
    has_err = "< 0" in generated_code
    details.append(
        CheckDetail(
            check_name="error_handling",
            passed=has_err,
            expected="Error checks on sensor API return values",
            actual="present" if has_err else "missing",
            check_type="constraint",
        )
    )

    return details
