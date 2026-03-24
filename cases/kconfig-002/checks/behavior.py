"""Behavioral checks for Zephyr BLE Mesh Kconfig fragment (metamorphic properties)."""

from embedeval.models import CheckDetail

_HALLUCINATED_CONFIGS = [
    "CONFIG_SECURE_MODE",
    "CONFIG_WIFI_BLE_COEX",
    "CONFIG_DEBUG_ENABLE",
    "CONFIG_NETWORK_STACK",
    "CONFIG_AUTO_INIT",
]


def _parse_config(generated_code: str) -> dict[str, str]:
    config: dict[str, str] = {}
    for line in generated_code.strip().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            config[key.strip()] = val.strip()
    return config


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate BLE Mesh Kconfig dependency chains and mutual exclusion invariants."""
    details: list[CheckDetail] = []
    config = _parse_config(generated_code)

    bt_enabled = config.get("CONFIG_BT") == "y"
    bt_hci_enabled = config.get("CONFIG_BT_HCI") == "y"
    bt_mesh_enabled = config.get("CONFIG_BT_MESH") == "y"
    bt_mesh_relay_enabled = config.get("CONFIG_BT_MESH_RELAY") == "y"
    bt_mesh_friend_enabled = config.get("CONFIG_BT_MESH_FRIEND") == "y"
    bt_mesh_low_power_enabled = config.get("CONFIG_BT_MESH_LOW_POWER") == "y"

    # Check 1: No hallucinated CONFIG options
    found_hallucinated = [opt for opt in _HALLUCINATED_CONFIGS if opt in generated_code]
    details.append(
        CheckDetail(
            check_name="no_hallucinated_config_options",
            passed=not found_hallucinated,
            expected="No hallucinated Zephyr CONFIG options",
            actual="clean" if not found_hallucinated else f"hallucinated: {found_hallucinated}",
            check_type="hallucination",
        )
    )

    # Check 2: Deprecated option conflict check
    has_newlib = config.get("CONFIG_NEWLIB_LIBC") == "y"
    has_minimal = config.get("CONFIG_MINIMAL_LIBC") == "y"
    no_deprecated_conflict = not (has_newlib and has_minimal)
    details.append(
        CheckDetail(
            check_name="no_newlib_minimal_libc_conflict",
            passed=no_deprecated_conflict,
            expected="CONFIG_NEWLIB_LIBC and CONFIG_MINIMAL_LIBC are mutually exclusive",
            actual=(
                "no conflict"
                if no_deprecated_conflict
                else "both CONFIG_NEWLIB_LIBC=y and CONFIG_MINIMAL_LIBC=y present (conflict)"
            ),
            check_type="constraint",
        )
    )

    # Check 3: Metamorphic: BT_MESH requires BT=y
    mesh_requires_bt = not (bt_mesh_enabled and not bt_enabled)
    details.append(
        CheckDetail(
            check_name="mesh_requires_bt",
            passed=mesh_requires_bt,
            expected="BT_MESH requires BT=y",
            actual=(
                f"BT={config.get('CONFIG_BT', 'n')}, "
                f"BT_MESH={config.get('CONFIG_BT_MESH', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Check 4: Metamorphic: BT requires BT_HCI=y
    bt_requires_hci = not (bt_enabled and not bt_hci_enabled)
    details.append(
        CheckDetail(
            check_name="bt_requires_hci",
            passed=bt_requires_hci,
            expected="BT requires BT_HCI=y",
            actual=(
                f"BT={config.get('CONFIG_BT', 'n')}, "
                f"BT_HCI={config.get('CONFIG_BT_HCI', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Check 5: Metamorphic: BT_MESH_RELAY requires BT_MESH=y
    relay_requires_mesh = not (bt_mesh_relay_enabled and not bt_mesh_enabled)
    details.append(
        CheckDetail(
            check_name="relay_requires_mesh",
            passed=relay_requires_mesh,
            expected="BT_MESH_RELAY requires BT_MESH=y",
            actual=(
                f"BT_MESH={config.get('CONFIG_BT_MESH', 'n')}, "
                f"BT_MESH_RELAY={config.get('CONFIG_BT_MESH_RELAY', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Check 6: Mutual exclusion: BT_MESH_FRIEND and BT_MESH_LOW_POWER cannot both be enabled
    no_friend_low_power = not (bt_mesh_friend_enabled and bt_mesh_low_power_enabled)
    details.append(
        CheckDetail(
            check_name="friend_low_power_mutual_exclusion",
            passed=no_friend_low_power,
            expected="BT_MESH_FRIEND and BT_MESH_LOW_POWER are mutually exclusive",
            actual=(
                f"FRIEND={config.get('CONFIG_BT_MESH_FRIEND', 'n')}, "
                f"LOW_POWER={config.get('CONFIG_BT_MESH_LOW_POWER', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Check 7: All required configs present AND enabled
    required_configs = [
        "CONFIG_BT",
        "CONFIG_BT_HCI",
        "CONFIG_BT_MESH",
        "CONFIG_BT_MESH_RELAY",
    ]
    all_present = all(config.get(k) == "y" for k in required_configs)
    details.append(
        CheckDetail(
            check_name="all_required_configs_enabled",
            passed=all_present,
            expected="BT, BT_HCI, BT_MESH, BT_MESH_RELAY all =y",
            actual=str({k: config.get(k, "missing") for k in required_configs}),
            check_type="exact_match",
        )
    )

    return details
