"""Behavioral checks for ESP-IDF ADC oneshot with calibration."""
from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []

    # Check 1: Calibration scheme created before raw_to_voltage conversion
    cali_pos = -1
    for fn in ["adc_cali_create_scheme_curve_fitting", "adc_cali_create_scheme_line_fitting"]:
        pos = generated_code.find(fn)
        if pos != -1 and (cali_pos == -1 or pos < cali_pos):
            cali_pos = pos

    voltage_pos = generated_code.find("adc_cali_raw_to_voltage")
    cali_before_voltage = cali_pos != -1 and voltage_pos != -1 and cali_pos < voltage_pos
    details.append(CheckDetail(
        check_name="calibration_before_raw_to_voltage",
        passed=cali_before_voltage,
        expected="Calibration scheme created before adc_cali_raw_to_voltage() is called",
        actual="correct order" if cali_before_voltage else "wrong order or missing calibration",
        check_type="constraint",
    ))

    # Check 2: Averaging — detect loop with numeric literal >= 5 OR a #define constant
    # used in a loop context. The task requires 10 samples.
    import re

    # Direct numeric literal in loop condition
    loop_literals = re.findall(r'(?:for|while)[^;{]*?(\d+)', generated_code)
    has_numeric_loop = any(int(n) >= 5 for n in loop_literals if n.isdigit())

    # Or a #define constant >= 5 used in a loop (e.g. SAMPLE_COUNT 10)
    define_match = re.search(r'#define\s+\w*(?:SAMPLE|COUNT|NUM|ITER|LOOP)\w*\s+(\d+)', generated_code,
                             re.IGNORECASE)
    has_define_loop = (
        define_match is not None
        and int(define_match.group(1)) >= 5
        and ("for" in generated_code or "while" in generated_code)
    )

    has_averaging = has_numeric_loop or has_define_loop
    details.append(CheckDetail(
        check_name="averaging_loop_present",
        passed=has_averaging,
        expected="Loop with at least 5 iterations for averaging (task requires 10)",
        actual="present" if has_averaging else "missing (single-shot read, no averaging)",
        check_type="constraint",
    ))

    # Check 3: adc_cali_raw_to_voltage used for millivolt conversion
    has_cali_convert = "adc_cali_raw_to_voltage" in generated_code
    details.append(CheckDetail(
        check_name="cali_raw_to_voltage_used",
        passed=has_cali_convert,
        expected="adc_cali_raw_to_voltage() used for calibrated millivolt conversion",
        actual="present" if has_cali_convert else "missing (raw scaling without calibration?)",
        check_type="constraint",
    ))

    # Check 4: Error handling on adc_oneshot_read
    read_pos = generated_code.find("adc_oneshot_read")
    post_read = generated_code[read_pos:read_pos + 200] if read_pos != -1 else ""
    has_read_check = "ESP_OK" in post_read or "!= ESP_OK" in post_read or "ret" in post_read
    details.append(CheckDetail(
        check_name="adc_read_error_checked",
        passed=has_read_check,
        expected="adc_oneshot_read() return value checked",
        actual="present" if has_read_check else "missing",
        check_type="constraint",
    ))

    # Check 5: ADC unit deleted (resource cleanup)
    has_cleanup = "adc_oneshot_del_unit" in generated_code
    details.append(CheckDetail(
        check_name="adc_unit_cleanup",
        passed=has_cleanup,
        expected="adc_oneshot_del_unit() called to release ADC unit",
        actual="present" if has_cleanup else "missing (resource leak)",
        check_type="constraint",
    ))

    # Check 6: ADC_ATTEN_DB_12 or ADC_ATTEN_DB_11 for 0-3.3V range
    has_correct_atten = (
        "ADC_ATTEN_DB_12" in generated_code
        or "ADC_ATTEN_DB_11" in generated_code
    )
    details.append(CheckDetail(
        check_name="correct_attenuation",
        passed=has_correct_atten,
        expected="ADC_ATTEN_DB_12 or ADC_ATTEN_DB_11 for 0-3.3V range",
        actual="present" if has_correct_atten else "missing (wrong attenuation for 3.3V range)",
        check_type="constraint",
    ))

    # Check: No cross-platform API contamination
    cross_plat = check_no_cross_platform_apis(generated_code, skip_platforms=["Linux_Userspace", "FreeRTOS"])
    details.append(CheckDetail(
        check_name="no_cross_platform_apis",
        passed=len(cross_plat) == 0,
        expected="No Arduino/STM32_HAL/POSIX APIs",
        actual="clean" if not cross_plat else f"found: {[a for a, _ in cross_plat]}",
        check_type="constraint",
    ))

    return details
