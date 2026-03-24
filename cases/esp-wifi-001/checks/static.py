"""Static checks for ESP-IDF WiFi station mode connect."""
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []

    details.append(CheckDetail(
        check_name="esp_wifi_header",
        passed="esp_wifi.h" in generated_code,
        expected="esp_wifi.h included",
        actual="present" if "esp_wifi.h" in generated_code else "missing",
        check_type="exact_match",
    ))

    details.append(CheckDetail(
        check_name="nvs_flash_header",
        passed="nvs_flash.h" in generated_code,
        expected="nvs_flash.h included (NVS required before WiFi)",
        actual="present" if "nvs_flash.h" in generated_code else "missing",
        check_type="exact_match",
    ))

    details.append(CheckDetail(
        check_name="esp_event_header",
        passed="esp_event.h" in generated_code,
        expected="esp_event.h included",
        actual="present" if "esp_event.h" in generated_code else "missing",
        check_type="exact_match",
    ))

    details.append(CheckDetail(
        check_name="app_main_defined",
        passed="app_main" in generated_code,
        expected="app_main() entry point",
        actual="present" if "app_main" in generated_code else "missing",
        check_type="exact_match",
    ))

    details.append(CheckDetail(
        check_name="esp_wifi_init_called",
        passed="esp_wifi_init" in generated_code,
        expected="esp_wifi_init() called",
        actual="present" if "esp_wifi_init" in generated_code else "missing",
        check_type="exact_match",
    ))

    details.append(CheckDetail(
        check_name="wifi_mode_sta",
        passed="WIFI_MODE_STA" in generated_code,
        expected="WIFI_MODE_STA set",
        actual="present" if "WIFI_MODE_STA" in generated_code else "missing",
        check_type="exact_match",
    ))

    details.append(CheckDetail(
        check_name="event_handler_registered",
        passed="esp_event_handler_register" in generated_code,
        expected="esp_event_handler_register() used",
        actual="present" if "esp_event_handler_register" in generated_code else "missing",
        check_type="exact_match",
    ))

    # Cross-platform hallucination checks
    # Note: "wifi_connect" is deliberately excluded — it is a substring of
    # "esp_wifi_connect" and would produce false positives on valid ESP-IDF code.
    zephyr_apis = ["net_if_up", "k_sleep", "DEVICE_DT_GET", "wifi_mgmt_connect"]
    found_zephyr = [api for api in zephyr_apis if api in generated_code]
    details.append(CheckDetail(
        check_name="no_zephyr_apis",
        passed=not found_zephyr,
        expected="No Zephyr networking APIs",
        actual="clean" if not found_zephyr else f"found Zephyr APIs: {found_zephyr}",
        check_type="hallucination",
    ))

    arduino_apis = ["WiFi.begin", "WiFi.status", "WiFiClient"]
    found_arduino = [api for api in arduino_apis if api in generated_code]
    details.append(CheckDetail(
        check_name="no_arduino_apis",
        passed=not found_arduino,
        expected="No Arduino WiFi APIs",
        actual="clean" if not found_arduino else f"found Arduino APIs: {found_arduino}",
        check_type="hallucination",
    ))

    return details
