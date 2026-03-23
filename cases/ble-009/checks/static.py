"""Static analysis checks for BLE bond management."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate BLE bond management code structure."""
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

    has_settings_h = "zephyr/settings/settings.h" in generated_code
    details.append(
        CheckDetail(
            check_name="settings_header",
            passed=has_settings_h,
            expected="zephyr/settings/settings.h included for persistent bonds",
            actual="present" if has_settings_h else "missing — bonds will not persist across reboots",
            check_type="exact_match",
        )
    )

    has_settings_load = "settings_load" in generated_code
    details.append(
        CheckDetail(
            check_name="settings_load_called",
            passed=has_settings_load,
            expected="settings_load() called to restore persistent bonds",
            actual="present" if has_settings_load else "missing — bonded devices not restored from flash",
            check_type="exact_match",
        )
    )

    has_foreach_bond = "bt_foreach_bond" in generated_code
    details.append(
        CheckDetail(
            check_name="bt_foreach_bond_called",
            passed=has_foreach_bond,
            expected="bt_foreach_bond() used to list bonds",
            actual="present" if has_foreach_bond else "missing",
            check_type="exact_match",
        )
    )

    has_bt_unpair = "bt_unpair" in generated_code
    details.append(
        CheckDetail(
            check_name="bt_unpair_called",
            passed=has_bt_unpair,
            expected="bt_unpair() used to remove bonds",
            actual="present" if has_bt_unpair else "missing",
            check_type="exact_match",
        )
    )

    has_bt_enable = "bt_enable" in generated_code
    details.append(
        CheckDetail(
            check_name="bt_enable_called",
            passed=has_bt_enable,
            expected="bt_enable() called before bond operations",
            actual="present" if has_bt_enable else "missing",
            check_type="exact_match",
        )
    )

    return details
