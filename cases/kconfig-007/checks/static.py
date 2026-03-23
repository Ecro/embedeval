"""Static analysis checks for Zephyr WiFi and BLE Coexistence Kconfig fragment."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate WiFi+BLE coexistence Kconfig fragment format and required options."""
    details: list[CheckDetail] = []
    lines = [
        line.strip()
        for line in generated_code.strip().splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    # Check 1: All lines use CONFIG_ prefix and contain =
    valid_format = all(
        line.startswith("CONFIG_") and "=" in line for line in lines
    )
    details.append(
        CheckDetail(
            check_name="kconfig_format",
            passed=valid_format,
            expected="All lines start with CONFIG_ and contain =",
            actual=f"{len(lines)} lines, format valid: {valid_format}",
            check_type="exact_match",
        )
    )

    # Check 2: CONFIG_WIFI=y present
    has_wifi = any("CONFIG_WIFI=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="wifi_enabled",
            passed=has_wifi,
            expected="CONFIG_WIFI=y",
            actual="present" if has_wifi else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: CONFIG_NET_L2_WIFI_MGMT=y present
    has_wifi_mgmt = any("CONFIG_NET_L2_WIFI_MGMT=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="wifi_mgmt_enabled",
            passed=has_wifi_mgmt,
            expected="CONFIG_NET_L2_WIFI_MGMT=y",
            actual="present" if has_wifi_mgmt else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: CONFIG_NETWORKING=y present (base dependency)
    has_networking = any("CONFIG_NETWORKING=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="networking_enabled",
            passed=has_networking,
            expected="CONFIG_NETWORKING=y",
            actual="present" if has_networking else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: CONFIG_BT=y present
    has_bt = any("CONFIG_BT=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="bt_enabled",
            passed=has_bt,
            expected="CONFIG_BT=y",
            actual="present" if has_bt else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: CONFIG_BT_COEX=y present
    has_bt_coex = any("CONFIG_BT_COEX=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="bt_coex_enabled",
            passed=has_bt_coex,
            expected="CONFIG_BT_COEX=y",
            actual="present" if has_bt_coex else "missing",
            check_type="exact_match",
        )
    )

    # Check 7: Hallucination trap — CONFIG_WIFI_BLE_COEX does not exist in Zephyr
    no_fake_coex = not any("CONFIG_WIFI_BLE_COEX=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="no_hallucinated_wifi_ble_coex",
            passed=no_fake_coex,
            expected="CONFIG_WIFI_BLE_COEX not present (does not exist in Zephyr)",
            actual="not present" if no_fake_coex else "CONFIG_WIFI_BLE_COEX=y found (hallucinated config)",
            check_type="constraint",
        )
    )

    return details
