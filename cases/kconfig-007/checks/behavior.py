"""Behavioral checks for Zephyr WiFi and BLE Coexistence Kconfig fragment."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate WiFi+BLE coexistence Kconfig dependency chains and hallucination invariants."""
    details: list[CheckDetail] = []
    config: dict[str, str] = {}
    for line in generated_code.strip().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            config[key.strip()] = val.strip()

    wifi_enabled = config.get("CONFIG_WIFI") == "y"
    wifi_mgmt_enabled = config.get("CONFIG_NET_L2_WIFI_MGMT") == "y"
    networking_enabled = config.get("CONFIG_NETWORKING") == "y"
    bt_enabled = config.get("CONFIG_BT") == "y"
    bt_coex_enabled = config.get("CONFIG_BT_COEX") == "y"
    fake_coex = config.get("CONFIG_WIFI_BLE_COEX") == "y"

    # Metamorphic: NET_L2_WIFI_MGMT requires WIFI=y
    wifi_mgmt_needs_wifi = not (wifi_mgmt_enabled and not wifi_enabled)
    details.append(
        CheckDetail(
            check_name="wifi_mgmt_requires_wifi",
            passed=wifi_mgmt_needs_wifi,
            expected="NET_L2_WIFI_MGMT requires WIFI=y",
            actual=(
                f"WIFI={config.get('CONFIG_WIFI', 'n')}, "
                f"NET_L2_WIFI_MGMT={config.get('CONFIG_NET_L2_WIFI_MGMT', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Metamorphic: WIFI requires NETWORKING=y
    wifi_needs_networking = not (wifi_enabled and not networking_enabled)
    details.append(
        CheckDetail(
            check_name="wifi_requires_networking",
            passed=wifi_needs_networking,
            expected="WIFI requires NETWORKING=y",
            actual=(
                f"NETWORKING={config.get('CONFIG_NETWORKING', 'n')}, "
                f"WIFI={config.get('CONFIG_WIFI', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Behavioral: BT_COEX requires both BT=y and WIFI=y to be meaningful
    coex_needs_both = not (bt_coex_enabled and not (bt_enabled and wifi_enabled))
    details.append(
        CheckDetail(
            check_name="bt_coex_requires_bt_and_wifi",
            passed=coex_needs_both,
            expected="BT_COEX meaningful only when both BT=y and WIFI=y",
            actual=(
                f"BT={config.get('CONFIG_BT', 'n')}, "
                f"WIFI={config.get('CONFIG_WIFI', 'n')}, "
                f"BT_COEX={config.get('CONFIG_BT_COEX', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Hallucination invariant: CONFIG_WIFI_BLE_COEX does not exist in Zephyr
    no_hallucinated_coex = not fake_coex
    details.append(
        CheckDetail(
            check_name="no_hallucinated_wifi_ble_coex",
            passed=no_hallucinated_coex,
            expected="CONFIG_WIFI_BLE_COEX not present (non-existent Zephyr option)",
            actual=(
                "not present"
                if no_hallucinated_coex
                else "CONFIG_WIFI_BLE_COEX=y found (hallucinated option)"
            ),
            check_type="constraint",
        )
    )

    # Summary: all required configs present
    required = ["CONFIG_NETWORKING", "CONFIG_WIFI", "CONFIG_NET_L2_WIFI_MGMT", "CONFIG_BT", "CONFIG_BT_COEX"]
    all_present = all(config.get(k) == "y" for k in required)
    details.append(
        CheckDetail(
            check_name="all_required_configs_enabled",
            passed=all_present,
            expected="NETWORKING, WIFI, NET_L2_WIFI_MGMT, BT, BT_COEX all =y",
            actual=str({k: config.get(k, "missing") for k in required}),
            check_type="exact_match",
        )
    )

    return details
