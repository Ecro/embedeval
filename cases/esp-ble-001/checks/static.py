"""Static checks for ESP-IDF BLE GATT server (Bluedroid stack)."""
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []

    # Check 1: BLE or BT header present
    has_bt_header = (
        "esp_bt.h" in generated_code
        or "esp_gap_ble_api.h" in generated_code
        or "esp_gatts_api.h" in generated_code
    )
    details.append(CheckDetail(
        check_name="ble_header",
        passed=has_bt_header,
        expected="esp_bt.h or esp_gap_ble_api.h or esp_gatts_api.h included",
        actual="present" if has_bt_header else "missing",
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

    # Check 3: Bluedroid stack initialization
    has_bluedroid = "esp_bluedroid_init" in generated_code
    details.append(CheckDetail(
        check_name="esp_bluedroid_init_called",
        passed=has_bluedroid,
        expected="esp_bluedroid_init() called to initialize Bluedroid stack",
        actual="present" if has_bluedroid else "missing",
        check_type="exact_match",
    ))

    # Check 4: GATTS app registered
    has_gatts_register = "esp_ble_gatts_app_register" in generated_code
    details.append(CheckDetail(
        check_name="gatts_app_register_called",
        passed=has_gatts_register,
        expected="esp_ble_gatts_app_register() called",
        actual="present" if has_gatts_register else "missing",
        check_type="exact_match",
    ))

    # Check 5: No Zephyr BT APIs (hallucination check)
    zephyr_bt_apis = ["bt_enable", "BT_GATT_SERVICE_DEFINE", "bt_le_adv_start", "BT_UUID_DECLARE"]
    found_zephyr = [api for api in zephyr_bt_apis if api in generated_code]
    details.append(CheckDetail(
        check_name="no_zephyr_bt_apis",
        passed=not found_zephyr,
        expected="No Zephyr BT APIs in ESP-IDF code",
        actual="clean" if not found_zephyr else f"found Zephyr BT APIs: {found_zephyr}",
        check_type="hallucination",
    ))

    # Check 6: No NimBLE APIs (wrong stack for this task)
    nimble_apis = ["nimble_port_init", "ble_gatts_count_cfg", "ble_hs_cfg"]
    found_nimble = [api for api in nimble_apis if api in generated_code]
    details.append(CheckDetail(
        check_name="no_nimble_apis",
        passed=not found_nimble,
        expected="No NimBLE APIs (task requires Bluedroid stack)",
        actual="clean" if not found_nimble else f"found NimBLE APIs: {found_nimble}",
        check_type="hallucination",
    ))

    return details
