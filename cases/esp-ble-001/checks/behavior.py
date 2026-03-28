"""Behavioral checks for ESP-IDF BLE GATT server (Bluedroid stack)."""
from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []

    # Check 1: NVS initialized before BLE
    nvs_pos = generated_code.find("nvs_flash_init")
    bt_pos = generated_code.find("esp_bt_controller_init")
    bluedroid_pos = generated_code.find("esp_bluedroid_init")

    bt_init_pos = min(p for p in [bt_pos, bluedroid_pos] if p != -1) if any(
        p != -1 for p in [bt_pos, bluedroid_pos]
    ) else -1

    nvs_before_bt = nvs_pos != -1 and bt_init_pos != -1 and nvs_pos < bt_init_pos
    details.append(CheckDetail(
        check_name="nvs_before_ble_init",
        passed=nvs_before_bt,
        expected="nvs_flash_init() called before BT controller/Bluedroid init",
        actual="correct order" if nvs_before_bt else "wrong order or missing NVS init",
        check_type="constraint",
    ))

    # Check 2: Both GAP and GATTS callbacks registered
    has_gap_cb = "esp_ble_gap_register_callback" in generated_code
    has_gatts_cb = "esp_ble_gatts_register_callback" in generated_code
    details.append(CheckDetail(
        check_name="gap_callback_registered",
        passed=has_gap_cb,
        expected="esp_ble_gap_register_callback() registered",
        actual="present" if has_gap_cb else "missing",
        check_type="constraint",
    ))
    details.append(CheckDetail(
        check_name="gatts_callback_registered",
        passed=has_gatts_cb,
        expected="esp_ble_gatts_register_callback() registered",
        actual="present" if has_gatts_cb else "missing",
        check_type="constraint",
    ))

    # Check 3: Advertising configured and started
    has_adv = (
        "esp_ble_gap_start_advertising" in generated_code
        or "esp_ble_gap_config_adv_data" in generated_code
    )
    details.append(CheckDetail(
        check_name="advertising_configured",
        passed=has_adv,
        expected="Advertising configured and started",
        actual="present" if has_adv else "missing",
        check_type="constraint",
    ))

    # Check 4: Write and Read events handled in GATTS callback
    has_write_evt = "ESP_GATTS_WRITE_EVT" in generated_code
    has_read_evt = "ESP_GATTS_READ_EVT" in generated_code
    details.append(CheckDetail(
        check_name="gatts_write_event_handled",
        passed=has_write_evt,
        expected="ESP_GATTS_WRITE_EVT handled in callback",
        actual="present" if has_write_evt else "missing",
        check_type="constraint",
    ))
    details.append(CheckDetail(
        check_name="gatts_read_event_handled",
        passed=has_read_evt,
        expected="ESP_GATTS_READ_EVT handled in callback",
        actual="present" if has_read_evt else "missing",
        check_type="constraint",
    ))

    # Check 5: BT controller enabled after init
    has_ctrl_enable = "esp_bt_controller_enable" in generated_code
    details.append(CheckDetail(
        check_name="bt_controller_enabled",
        passed=has_ctrl_enable,
        expected="esp_bt_controller_enable() called after init",
        actual="controller enabled" if has_ctrl_enable else "controller not enabled (dead stack)",
        check_type="constraint",
    ))

    # Check 6: Bluedroid enabled after init
    has_bluedroid_enable = "esp_bluedroid_enable" in generated_code
    details.append(CheckDetail(
        check_name="bluedroid_enabled",
        passed=has_bluedroid_enable,
        expected="esp_bluedroid_enable() called after init",
        actual="bluedroid enabled" if has_bluedroid_enable else "bluedroid not enabled (dead stack)",
        check_type="constraint",
    ))

    # Check 7: No NimBLE APIs used
    nimble_apis = ["nimble_port_run", "ble_svc_gap_init", "ble_gatts_add_svcs"]
    found_nimble = [api for api in nimble_apis if api in generated_code]
    details.append(CheckDetail(
        check_name="no_nimble_apis",
        passed=not found_nimble,
        expected="No NimBLE APIs (task requires Bluedroid)",
        actual="clean" if not found_nimble else f"found NimBLE: {found_nimble}",
        check_type="hallucination",
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
