"""Behavioral checks for hardware counter with alarm application."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate counter alarm behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: counter_start called before counter_set_channel_alarm
    # AI failure: setting alarm before starting counter
    start_pos = generated_code.find("counter_start")
    alarm_pos = generated_code.find("counter_set_channel_alarm")
    start_before_alarm = (
        start_pos != -1 and alarm_pos != -1 and start_pos < alarm_pos
    )
    details.append(
        CheckDetail(
            check_name="counter_started_before_alarm",
            passed=start_before_alarm,
            expected="counter_start() called before counter_set_channel_alarm()",
            actual="correct order" if start_before_alarm else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: Alarm callback is assigned (not NULL)
    # AI failure: omitting callback entirely or setting callback=NULL
    alarm_cfg_section = ""
    cfg_match = re.search(
        r"counter_alarm_cfg[^;]*=\s*\{([^}]*)\}", generated_code, re.DOTALL
    )
    if cfg_match:
        alarm_cfg_section = cfg_match.group(1)
    callback_assigned = (
        ".callback" in alarm_cfg_section
        and "NULL" not in alarm_cfg_section.split(".callback")[1].split(",")[0]
        if ".callback" in alarm_cfg_section
        else "callback" in generated_code and "alarm_callback" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="alarm_callback_not_null",
            passed=bool(callback_assigned),
            expected="Alarm callback assigned (not NULL) in counter_alarm_cfg",
            actual="assigned" if callback_assigned else "NULL or missing",
            check_type="constraint",
        )
    )

    # Check 3: Uses counter_us_to_ticks for tick conversion (not hardcoded ticks)
    # AI failure: using raw tick values or k_ms_to_cyc macros
    has_tick_conversion = "counter_us_to_ticks" in generated_code
    details.append(
        CheckDetail(
            check_name="uses_tick_conversion",
            passed=has_tick_conversion,
            expected="counter_us_to_ticks() used for time-to-ticks conversion",
            actual="present" if has_tick_conversion else "missing - may use hardcoded ticks",
            check_type="constraint",
        )
    )

    # Check 4: device_is_ready called before counter operations
    ready_pos = generated_code.find("device_is_ready")
    start_pos2 = generated_code.find("counter_start")
    ready_before_start = (
        ready_pos != -1 and start_pos2 != -1 and ready_pos < start_pos2
    )
    details.append(
        CheckDetail(
            check_name="ready_check_before_counter_ops",
            passed=ready_before_start,
            expected="device_is_ready() checked before counter_start()",
            actual="correct order" if ready_before_start else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 5: Alarm callback has correct signature (device, chan_id, ticks, user_data)
    has_alarm_sig = bool(
        re.search(
            r"\w+\s*\(\s*const\s+struct\s+device\s*\*",
            generated_code,
        )
    )
    details.append(
        CheckDetail(
            check_name="alarm_callback_signature",
            passed=has_alarm_sig,
            expected="Alarm callback takes const struct device * as first parameter",
            actual="correct" if has_alarm_sig else "wrong or missing signature",
            check_type="exact_match",
        )
    )

    return details
