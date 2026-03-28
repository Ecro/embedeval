"""Behavioral checks for sensor power management (low-power mode)."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate sensor power management behavioral properties."""
    details: list[CheckDetail] = []

    # Find the read position: prefer read_sensor() call (if present) or last
    # sensor_sample_fetch call.  Using the last occurrence avoids matching the
    # function *definition* which appears before main().
    read_pos = generated_code.rfind("read_sensor(")
    if read_pos == -1:
        read_pos = generated_code.rfind("sensor_sample_fetch")

    # Find low-power set call: the last set_sampling_freq(dev, 0) or equivalent
    low_power_pos = -1
    for pattern in ["set_sampling_freq(dev, 0)", ".val1 = 0", "freq_hz = 0"]:
        p = generated_code.rfind(pattern)
        if p != -1 and p > low_power_pos:
            low_power_pos = p

    # Find normal-mode set call: the first set_sampling_freq call AFTER the
    # function definition (i.e., inside main's loop).  We look for the first
    # occurrence of a call with a non-zero argument that appears in main() —
    # heuristic: find after the last closing brace of helper functions by
    # scanning for "set_sampling_freq(dev, " with a digit != 0.
    import re
    normal_mode_pos = -1
    for m in re.finditer(r'set_sampling_freq\s*\(\s*\w+\s*,\s*([1-9]\d*)\s*\)', generated_code):
        normal_mode_pos = m.start()
        break  # first non-zero call

    # Check 1: Low-power mode set AFTER the read, not before
    # (LLM failure: setting freq=0 before read, so sensor is idle when read starts)
    details.append(
        CheckDetail(
            check_name="low_power_after_read",
            passed=read_pos != -1 and low_power_pos != -1 and read_pos < low_power_pos,
            expected="Low-power mode (freq=0) set AFTER sensor read",
            actual="correct" if (read_pos != -1 and low_power_pos != -1 and read_pos < low_power_pos)
                   else "WRONG ORDER — sensor put to sleep before reading data!",
            check_type="constraint",
        )
    )

    # Check 2: Normal mode set BEFORE the read
    # (LLM failure: reading while sensor is still in low-power mode)
    details.append(
        CheckDetail(
            check_name="normal_mode_before_read",
            passed=normal_mode_pos != -1 and read_pos != -1 and normal_mode_pos < read_pos,
            expected="Normal sampling mode set BEFORE sensor read",
            actual="correct" if (normal_mode_pos != -1 and read_pos != -1 and normal_mode_pos < read_pos)
                   else "WRONG ORDER or missing — reading while sensor may be in low-power mode!",
            check_type="constraint",
        )
    )

    # Check 3: sensor_attr_set used (not raw register write)
    # (LLM failure: directly calling i2c_reg_write_byte to set a power register)
    has_attr_set = "sensor_attr_set" in generated_code
    details.append(
        CheckDetail(
            check_name="attr_set_not_raw_register",
            passed=has_attr_set,
            expected="sensor_attr_set() used for power mode control (not raw register write)",
            actual="correct" if has_attr_set
                   else "missing — power mode not controlled via sensor attribute API",
            check_type="constraint",
        )
    )

    # Check 4: Loop structure present (read/sleep cycle repeated)
    # (LLM failure: single read without any loop)
    has_loop = "for (" in generated_code or "while (" in generated_code
    details.append(
        CheckDetail(
            check_name="read_sleep_cycle_loop",
            passed=has_loop,
            expected="Loop structure for periodic read/low-power cycle",
            actual="present" if has_loop else "missing (single read, no duty cycle)",
            check_type="constraint",
        )
    )

    # Check 5: k_sleep used for idle period between reads
    has_sleep = "k_sleep" in generated_code or "k_msleep" in generated_code
    details.append(
        CheckDetail(
            check_name="sleep_between_reads",
            passed=has_sleep,
            expected="k_sleep/k_msleep used for idle period between sensor reads",
            actual="present" if has_sleep else "missing (busy-polling without sleep)",
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
