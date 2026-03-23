"""Static analysis checks for Zephyr BLE Mesh Kconfig fragment."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate BLE Mesh Kconfig fragment format and required options."""
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

    # Check 2: CONFIG_BT=y present
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

    # Check 3: CONFIG_BT_HCI=y present (dependency for BT)
    has_bt_hci = any("CONFIG_BT_HCI=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="bt_hci_enabled",
            passed=has_bt_hci,
            expected="CONFIG_BT_HCI=y",
            actual="present" if has_bt_hci else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: CONFIG_BT_MESH=y present
    has_bt_mesh = any("CONFIG_BT_MESH=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="bt_mesh_enabled",
            passed=has_bt_mesh,
            expected="CONFIG_BT_MESH=y",
            actual="present" if has_bt_mesh else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: CONFIG_BT_MESH_RELAY=y present
    has_relay = any("CONFIG_BT_MESH_RELAY=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="bt_mesh_relay_enabled",
            passed=has_relay,
            expected="CONFIG_BT_MESH_RELAY=y",
            actual="present" if has_relay else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: FRIEND and LOW_POWER are not both enabled (mutual exclusion)
    has_friend = any("CONFIG_BT_MESH_FRIEND=y" in line for line in lines)
    has_low_power = any("CONFIG_BT_MESH_LOW_POWER=y" in line for line in lines)
    no_conflict = not (has_friend and has_low_power)
    details.append(
        CheckDetail(
            check_name="no_friend_low_power_conflict",
            passed=no_conflict,
            expected="BT_MESH_FRIEND and BT_MESH_LOW_POWER not both enabled",
            actual=(
                "conflict: both enabled"
                if not no_conflict
                else "no conflict present"
            ),
            check_type="constraint",
        )
    )

    return details
