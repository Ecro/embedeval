"""Static checks for ESP-IDF ADC oneshot with calibration."""
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []

    # Check 1: ADC oneshot header present (new v5.x API)
    has_adc_header = (
        "esp_adc/adc_oneshot.h" in generated_code
        or "adc_oneshot.h" in generated_code
    )
    details.append(CheckDetail(
        check_name="adc_oneshot_header",
        passed=has_adc_header,
        expected="esp_adc/adc_oneshot.h included (ESP-IDF v5.x oneshot API)",
        actual="present" if has_adc_header else "missing",
        check_type="exact_match",
    ))

    # Check 2: app_main entry point
    details.append(CheckDetail(
        check_name="app_main_defined",
        passed="app_main" in generated_code,
        expected="app_main() entry point",
        actual="present" if "app_main" in generated_code else "missing",
        check_type="exact_match",
    ))

    # Check 3: New oneshot API used (not deprecated adc1_get_raw)
    has_oneshot_api = "adc_oneshot_read" in generated_code
    details.append(CheckDetail(
        check_name="adc_oneshot_read_used",
        passed=has_oneshot_api,
        expected="adc_oneshot_read() called (v5.x API)",
        actual="present" if has_oneshot_api else "missing (using deprecated adc1_get_raw?)",
        check_type="exact_match",
    ))

    # Check 4: Deprecated API must NOT be used
    uses_deprecated = "adc1_get_raw" in generated_code
    details.append(CheckDetail(
        check_name="no_deprecated_adc1_get_raw",
        passed=not uses_deprecated,
        expected="No deprecated adc1_get_raw() call",
        actual="clean" if not uses_deprecated else "found deprecated adc1_get_raw",
        check_type="hallucination",
    ))

    # Check 5: No Zephyr sensor APIs
    zephyr_apis = ["sensor_sample_fetch", "sensor_channel_get", "DEVICE_DT_GET", "k_sleep", "printk"]
    found = [api for api in zephyr_apis if api in generated_code]
    details.append(CheckDetail(
        check_name="no_zephyr_sensor_apis",
        passed=not found,
        expected="No Zephyr sensor APIs in ESP-IDF code",
        actual="clean" if not found else f"found Zephyr APIs: {found}",
        check_type="hallucination",
    ))

    return details
