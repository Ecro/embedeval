"""Behavioral checks for ADC oversampling application."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate ADC behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: adc_channel_setup called before adc_read (correct ordering)
    setup_pos = generated_code.find("adc_channel_setup")
    read_pos = generated_code.find("adc_read")
    order_ok = setup_pos != -1 and read_pos != -1 and setup_pos < read_pos
    details.append(
        CheckDetail(
            check_name="setup_before_read",
            passed=order_ok,
            expected="adc_channel_setup called before adc_read",
            actual="correct order" if order_ok else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: Resolution is a valid value (8, 10, 12, 14, 16)
    import re
    res_match = re.search(r"resolution\s*=\s*(\d+)", generated_code)
    valid_resolutions = {8, 10, 12, 14, 16}
    res_ok = bool(res_match and int(res_match.group(1)) in valid_resolutions)
    details.append(
        CheckDetail(
            check_name="valid_adc_resolution",
            passed=res_ok,
            expected="ADC resolution set to valid value (8/10/12/14/16 bits)",
            actual=res_match.group(0) if res_match else "not set",
            check_type="constraint",
        )
    )

    # Check 3: Oversampling configured before read (setup struct before adc_read)
    oversamp_pos = generated_code.find("oversampling")
    oversamp_before_read = oversamp_pos != -1 and read_pos != -1 and oversamp_pos < read_pos
    details.append(
        CheckDetail(
            check_name="oversampling_before_read",
            passed=oversamp_before_read,
            expected="oversampling field configured before adc_read()",
            actual="correct order" if oversamp_before_read else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 4: Sample buffer defined with positive size
    buf_match = re.search(r"int16_t\s+\w+\[(\d+)\]", generated_code)
    buf_ok = bool(buf_match and int(buf_match.group(1)) > 0)
    details.append(
        CheckDetail(
            check_name="sample_buffer_nonzero",
            passed=buf_ok,
            expected="int16_t sample buffer declared with positive size",
            actual="present" if buf_ok else "missing or zero-sized",
            check_type="constraint",
        )
    )

    # Check 5: device_is_ready check present
    has_ready = "device_is_ready" in generated_code
    details.append(
        CheckDetail(
            check_name="device_ready_check",
            passed=has_ready,
            expected="device_is_ready() called before ADC operations",
            actual="present" if has_ready else "missing",
            check_type="constraint",
        )
    )

    # Check 6: Reads in a loop with sleep (not single shot)
    has_loop = "while" in generated_code or "for" in generated_code
    has_sleep = "k_sleep" in generated_code
    details.append(
        CheckDetail(
            check_name="periodic_read_with_sleep",
            passed=has_loop and has_sleep,
            expected="ADC read in loop with k_sleep between reads",
            actual=f"loop={has_loop}, sleep={has_sleep}",
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
