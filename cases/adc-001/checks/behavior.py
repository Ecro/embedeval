"""Behavioral checks for ADC single channel read application."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate ADC behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: Device ready check before ADC operations (AI failure: skipping this)
    has_ready_check = any(
        p in generated_code
        for p in ["adc_is_ready_dt", "device_is_ready"]
    )
    details.append(
        CheckDetail(
            check_name="device_ready_check",
            passed=has_ready_check,
            expected="adc_is_ready_dt() or device_is_ready() called before ADC operations",
            actual="present" if has_ready_check else "missing",
            check_type="constraint",
        )
    )

    # Check 2: Channel setup called before read (AI failure: calling adc_read without setup)
    setup_pos = generated_code.find("adc_channel_setup")
    read_pos = min(
        (generated_code.find(p) for p in ["adc_read_dt", "adc_read"] if generated_code.find(p) != -1),
        default=-1,
    )
    channel_setup_before_read = setup_pos != -1 and read_pos != -1 and setup_pos < read_pos
    details.append(
        CheckDetail(
            check_name="channel_setup_before_read",
            passed=channel_setup_before_read,
            expected="adc_channel_setup_dt() called before adc_read()",
            actual="correct order" if channel_setup_before_read else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 3: Millivolt conversion called (AI failure: printing raw ADC counts as volts)
    has_mv_conversion = any(
        p in generated_code
        for p in ["adc_raw_to_millivolts_dt", "adc_raw_to_millivolts"]
    )
    details.append(
        CheckDetail(
            check_name="millivolt_conversion_called",
            passed=has_mv_conversion,
            expected="adc_raw_to_millivolts_dt() called to convert raw value",
            actual="present" if has_mv_conversion else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Buffer referenced in sequence struct (AI failure: wrong resolution / no buffer)
    has_buffer_in_sequence = ".buffer" in generated_code and "buf" in generated_code
    details.append(
        CheckDetail(
            check_name="buffer_linked_to_sequence",
            passed=has_buffer_in_sequence,
            expected=".buffer field set in adc_sequence struct",
            actual="present" if has_buffer_in_sequence else "missing",
            check_type="constraint",
        )
    )

    # Check 5: Read happens in a loop with sleep (periodic sampling)
    has_loop = any(p in generated_code for p in ["while (1)", "while(1)", "for (;;)", "for(;;)"])
    has_sleep = any(p in generated_code for p in ["k_sleep", "k_msleep"])
    details.append(
        CheckDetail(
            check_name="periodic_sampling_loop",
            passed=has_loop and has_sleep,
            expected="Infinite loop with k_sleep for periodic sampling",
            actual="present" if (has_loop and has_sleep) else "missing loop or sleep",
            check_type="exact_match",
        )
    )

    # Check 6: adc_read or adc_read_dt return value checked for errors
    has_read_check = any(
        p in generated_code
        for p in ["if (err", "if (ret", "if (rc", "< 0"]
    )
    details.append(
        CheckDetail(
            check_name="read_return_value_checked",
            passed=has_read_check,
            expected="adc_read return value checked for errors",
            actual="checked" if has_read_check else "unchecked",
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
