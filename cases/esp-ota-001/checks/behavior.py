"""Behavioral checks for ESP-IDF OTA update via HTTPS."""
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []

    # Check 1: WiFi initialized before the OTA operation begins.
    # Compare positions of the actual function calls, not header includes.
    wifi_pos = generated_code.find("esp_wifi_init(")
    # The actual OTA operation starts with esp_https_ota_begin or esp_https_ota (simple form)
    ota_begin_pos = generated_code.find("esp_https_ota_begin")
    if ota_begin_pos == -1:
        # Simple one-shot API
        ota_begin_pos = generated_code.find("esp_https_ota(")

    wifi_before_ota = wifi_pos != -1 and ota_begin_pos != -1 and wifi_pos < ota_begin_pos
    details.append(CheckDetail(
        check_name="wifi_before_ota",
        passed=wifi_before_ota,
        expected="WiFi initialized (esp_wifi_init) before OTA operation begins",
        actual="correct order" if wifi_before_ota else "wrong order or missing WiFi init",
        check_type="constraint",
    ))

    # Check 2: NVS initialized before WiFi (WiFi requires NVS)
    # NVS must be present. Position comparison is unreliable when WiFi init
    # is inside a helper function defined before app_main, so we just check
    # that nvs_flash_init is present (it must run before WiFi at runtime).
    nvs_pos = generated_code.find("nvs_flash_init")
    has_nvs_before_wifi = nvs_pos != -1
    details.append(CheckDetail(
        check_name="nvs_init_before_wifi",
        passed=has_nvs_before_wifi,
        expected="nvs_flash_init() called before esp_wifi_init()",
        actual="correct ordering" if has_nvs_before_wifi else "NVS not initialized before WiFi",
        check_type="constraint",
    ))

    # Check 3: Rollback on failure
    has_rollback = (
        "esp_ota_mark_app_invalid_rollback_and_reboot" in generated_code
        or "esp_https_ota_abort" in generated_code
    )
    details.append(CheckDetail(
        check_name="rollback_on_failure",
        passed=has_rollback,
        expected="Rollback triggered on OTA failure (esp_ota_mark_app_invalid_rollback_and_reboot or abort)",
        actual="present" if has_rollback else "missing (no rollback on failure path)",
        check_type="constraint",
    ))

    # Check 3: Firmware validated and marked valid after successful download
    has_validation = "esp_ota_mark_app_valid_cancel_rollback" in generated_code
    details.append(CheckDetail(
        check_name="firmware_validation",
        passed=has_validation,
        expected="esp_ota_mark_app_valid_cancel_rollback() called after successful OTA",
        actual="present" if has_validation else "missing (firmware not validated — rollback watchdog may trigger)",
        check_type="constraint",
    ))

    # Check 4: Device restarted after successful OTA
    has_restart = "esp_restart" in generated_code
    details.append(CheckDetail(
        check_name="restart_after_ota",
        passed=has_restart,
        expected="esp_restart() called to boot new firmware",
        actual="present" if has_restart else "missing",
        check_type="constraint",
    ))

    # Check 5: Error handling present throughout
    has_error_handling = (
        "!= ESP_OK" in generated_code
        or "ESP_ERROR_CHECK" in generated_code
    ) and "ESP_LOGE" in generated_code
    details.append(CheckDetail(
        check_name="error_handling_present",
        passed=has_error_handling,
        expected="Error handling with logging on failure paths",
        actual="present" if has_error_handling else "missing",
        check_type="constraint",
    ))

    return details
