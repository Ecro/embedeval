"""Static analysis checks for BLE advertising with manufacturer data."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate BLE manufacturer data advertising structure."""
    details: list[CheckDetail] = []

    has_bt_h = "zephyr/bluetooth/bluetooth.h" in generated_code
    details.append(
        CheckDetail(
            check_name="bluetooth_header",
            passed=has_bt_h,
            expected="zephyr/bluetooth/bluetooth.h included",
            actual="present" if has_bt_h else "missing",
            check_type="exact_match",
        )
    )

    has_manufacturer_data = "BT_DATA_MANUFACTURER_DATA" in generated_code
    details.append(
        CheckDetail(
            check_name="manufacturer_data_type_used",
            passed=has_manufacturer_data,
            expected="BT_DATA_MANUFACTURER_DATA type used in ad[]",
            actual="present" if has_manufacturer_data else "missing — manufacturer data not set",
            check_type="exact_match",
        )
    )

    has_bt_data_bytes = "BT_DATA_BYTES" in generated_code
    details.append(
        CheckDetail(
            check_name="bt_data_bytes_macro_used",
            passed=has_bt_data_bytes,
            expected="BT_DATA_BYTES macro used to build advertising data",
            actual="present" if has_bt_data_bytes else "missing",
            check_type="exact_match",
        )
    )

    has_bt_enable = "bt_enable" in generated_code
    details.append(
        CheckDetail(
            check_name="bt_enable_called",
            passed=has_bt_enable,
            expected="bt_enable() called",
            actual="present" if has_bt_enable else "missing",
            check_type="exact_match",
        )
    )

    has_adv_start = "bt_le_adv_start" in generated_code
    details.append(
        CheckDetail(
            check_name="bt_le_adv_start_called",
            passed=has_adv_start,
            expected="bt_le_adv_start() called",
            actual="present" if has_adv_start else "missing",
            check_type="exact_match",
        )
    )

    return details
