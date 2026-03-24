"""Behavioral checks for ESP-IDF WiFi station mode connect."""
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []

    # Check 1: NVS initialized before WiFi (nvs_flash_init appears before esp_wifi_init)
    nvs_pos = generated_code.find("nvs_flash_init")
    wifi_pos = generated_code.find("esp_wifi_init")
    nvs_before_wifi = nvs_pos != -1 and (wifi_pos == -1 or nvs_pos < wifi_pos)
    details.append(CheckDetail(
        check_name="nvs_initialized_before_wifi",
        passed=nvs_before_wifi,
        expected="nvs_flash_init() called before esp_wifi_init()",
        actual="correct order" if nvs_before_wifi else "wrong order or nvs_flash_init missing",
        check_type="constraint",
    ))

    # Check 2: NVS error handling includes page/version cases
    has_nvs_recovery = (
        "ESP_ERR_NVS_NO_FREE_PAGES" in generated_code
        or "ESP_ERR_NVS_NEW_VERSION_FOUND" in generated_code
    )
    details.append(CheckDetail(
        check_name="nvs_error_recovery",
        passed=has_nvs_recovery,
        expected="Handle ESP_ERR_NVS_NO_FREE_PAGES / ESP_ERR_NVS_NEW_VERSION_FOUND",
        actual="present" if has_nvs_recovery else "missing (NVS can fail on first boot)",
        check_type="constraint",
    ))

    # Check 3: esp_netif_init called
    has_netif_init = "esp_netif_init" in generated_code
    details.append(CheckDetail(
        check_name="esp_netif_init_called",
        passed=has_netif_init,
        expected="esp_netif_init() called for network interface",
        actual="present" if has_netif_init else "missing",
        check_type="constraint",
    ))

    # Check 4: Reconnect on disconnect handled in event handler
    has_reconnect = "esp_wifi_connect" in generated_code
    details.append(CheckDetail(
        check_name="reconnect_on_disconnect",
        passed=has_reconnect,
        expected="esp_wifi_connect() called (reconnect logic or initial connect)",
        actual="present" if has_reconnect else "missing",
        check_type="constraint",
    ))

    # Check 5: WIFI_INIT_CONFIG_DEFAULT macro used for safe initialization
    has_default_cfg = "WIFI_INIT_CONFIG_DEFAULT" in generated_code
    details.append(CheckDetail(
        check_name="wifi_init_config_default",
        passed=has_default_cfg,
        expected="WIFI_INIT_CONFIG_DEFAULT() macro for safe wifi_init_config_t",
        actual="present" if has_default_cfg else "missing (manual config risks uninitialized fields)",
        check_type="constraint",
    ))

    # Check 6: esp_wifi_start called
    has_wifi_start = "esp_wifi_start" in generated_code
    details.append(CheckDetail(
        check_name="esp_wifi_start_called",
        passed=has_wifi_start,
        expected="esp_wifi_start() called to activate WiFi",
        actual="present" if has_wifi_start else "missing",
        check_type="constraint",
    ))

    # Check 7: No Arduino WiFi APIs
    arduino_apis = ["WiFi.begin", "WiFi.status", "WiFiClient", "WiFiServer"]
    found_arduino = [api for api in arduino_apis if api in generated_code]
    details.append(CheckDetail(
        check_name="no_arduino_wifi_apis",
        passed=not found_arduino,
        expected="No Arduino WiFi APIs",
        actual="clean" if not found_arduino else f"found: {found_arduino}",
        check_type="hallucination",
    ))

    return details
