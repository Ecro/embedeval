"""Behavioral checks for sensor data-ready trigger."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate sensor trigger behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: device_is_ready before sensor_trigger_set
    # (LLM failure: setting trigger on an unconfirmed-ready device)
    ready_pos = generated_code.find("device_is_ready")
    trigger_pos = generated_code.find("sensor_trigger_set")
    details.append(
        CheckDetail(
            check_name="ready_before_trigger_set",
            passed=ready_pos != -1 and trigger_pos != -1 and ready_pos < trigger_pos,
            expected="device_is_ready() before sensor_trigger_set()",
            actual="correct" if (ready_pos != -1 and trigger_pos != -1 and ready_pos < trigger_pos) else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: Callback contains sensor_sample_fetch
    # (LLM failure: empty callback or callback that only prints without fetching)
    has_fetch_in_callback = "sensor_sample_fetch" in generated_code
    details.append(
        CheckDetail(
            check_name="fetch_in_callback",
            passed=has_fetch_in_callback,
            expected="sensor_sample_fetch() called inside trigger callback",
            actual="present" if has_fetch_in_callback else "missing (callback does not fetch data)",
            check_type="constraint",
        )
    )

    # Check 3: Uses SENSOR_TRIG_DATA_READY (not wrong trigger type)
    # (LLM failure: using SENSOR_TRIG_THRESHOLD or SENSOR_TRIG_TIMER instead)
    has_data_ready = "SENSOR_TRIG_DATA_READY" in generated_code
    details.append(
        CheckDetail(
            check_name="correct_trigger_type",
            passed=has_data_ready,
            expected="SENSOR_TRIG_DATA_READY trigger type",
            actual="correct" if has_data_ready else "wrong trigger type used",
            check_type="exact_match",
        )
    )

    # Check 4: Error handling on sensor_trigger_set
    trigger_set_pos = generated_code.find("sensor_trigger_set")
    has_trigger_err = trigger_set_pos != -1 and (
        "< 0" in generated_code[trigger_set_pos:trigger_set_pos + 200]
        or "!= 0" in generated_code[trigger_set_pos:trigger_set_pos + 200]
    )
    details.append(
        CheckDetail(
            check_name="trigger_set_error_handling",
            passed=has_trigger_err,
            expected="Return value of sensor_trigger_set() checked",
            actual="present" if has_trigger_err else "missing",
            check_type="constraint",
        )
    )

    # Check 5: Main sleeps forever after trigger setup (event-driven, not polling)
    # (LLM failure: busy-polling in a loop instead of using trigger)
    has_sleep_forever = "K_FOREVER" in generated_code
    details.append(
        CheckDetail(
            check_name="event_driven_sleep",
            passed=has_sleep_forever,
            expected="k_sleep(K_FOREVER) after trigger setup (event-driven)",
            actual="present" if has_sleep_forever else "missing (polling instead of event-driven?)",
            check_type="constraint",
        )
    )

    return details
