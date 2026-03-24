"""Static checks for ESP-IDF OTA update via HTTPS."""
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []

    # Check 1: OTA header present
    has_ota_header = (
        "esp_https_ota.h" in generated_code
        or "esp_ota_ops.h" in generated_code
    )
    details.append(CheckDetail(
        check_name="ota_header",
        passed=has_ota_header,
        expected="esp_https_ota.h or esp_ota_ops.h included",
        actual="present" if has_ota_header else "missing",
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

    # Check 3: WiFi initialization present
    has_wifi_init = (
        "esp_wifi_init" in generated_code
        or "wifi_init_config_t" in generated_code
    )
    details.append(CheckDetail(
        check_name="wifi_init_present",
        passed=has_wifi_init,
        expected="WiFi initialization (esp_wifi_init or wifi_init_config_t)",
        actual="present" if has_wifi_init else "missing",
        check_type="exact_match",
    ))

    # Check 4: OTA URL used
    has_url = "https://example.com/firmware.bin" in generated_code
    details.append(CheckDetail(
        check_name="ota_url_present",
        passed=has_url,
        expected="OTA URL https://example.com/firmware.bin present",
        actual="present" if has_url else "missing",
        check_type="exact_match",
    ))

    # Check 5: No Zephyr APIs
    zephyr_apis = ["dfu_target", "boot_request_upgrade", "k_sleep", "DEVICE_DT_GET", "printk"]
    found = [api for api in zephyr_apis if api in generated_code]
    details.append(CheckDetail(
        check_name="no_zephyr_apis",
        passed=not found,
        expected="No Zephyr OTA/DFU APIs in ESP-IDF code",
        actual="clean" if not found else f"found Zephyr APIs: {found}",
        check_type="hallucination",
    ))

    return details
