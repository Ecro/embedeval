"""Behavioral checks for Basic MCUboot Logging Kconfig fragment."""

from embedeval.models import CheckDetail


def _parse_config(generated_code: str) -> dict[str, str]:
    config: dict[str, str] = {}
    for line in generated_code.strip().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            config[key.strip()] = val.strip()
    return config


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate basic MCUboot logging Kconfig dependency chains and conflict invariants."""
    details: list[CheckDetail] = []
    config = _parse_config(generated_code)

    mcuboot_enabled = config.get("CONFIG_BOOTLOADER_MCUBOOT") == "y"
    log_enabled = config.get("CONFIG_LOG") == "y"
    log_level_dbg_enabled = config.get("CONFIG_MCUBOOT_LOG_LEVEL_DBG") == "y"
    boot_banner_enabled = config.get("CONFIG_BOOT_BANNER") == "y"
    log_minimal_enabled = config.get("CONFIG_LOG_MINIMAL") == "y"

    # Metamorphic: MCUBOOT_LOG_LEVEL_DBG requires LOG=y
    log_level_needs_log = not (log_level_dbg_enabled and not log_enabled)
    details.append(
        CheckDetail(
            check_name="mcuboot_log_level_dbg_requires_log",
            passed=log_level_needs_log,
            expected="MCUBOOT_LOG_LEVEL_DBG requires LOG=y",
            actual=(
                f"LOG={config.get('CONFIG_LOG', 'n')}, "
                f"MCUBOOT_LOG_LEVEL_DBG={config.get('CONFIG_MCUBOOT_LOG_LEVEL_DBG', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Conflict: LOG_MINIMAL suppresses debug output — cannot coexist with LOG_LEVEL_DBG
    no_minimal_conflict = not (log_minimal_enabled and log_level_dbg_enabled)
    details.append(
        CheckDetail(
            check_name="log_minimal_log_level_dbg_mutual_exclusion",
            passed=no_minimal_conflict,
            expected="LOG_MINIMAL and MCUBOOT_LOG_LEVEL_DBG are incompatible",
            actual=(
                "no conflict"
                if no_minimal_conflict
                else "both LOG_MINIMAL=y and MCUBOOT_LOG_LEVEL_DBG=y set (LOG_MINIMAL suppresses debug)"
            ),
            check_type="constraint",
        )
    )

    # Summary: all required configs present
    required = [
        "CONFIG_BOOTLOADER_MCUBOOT",
        "CONFIG_LOG",
        "CONFIG_BOOT_BANNER",
        "CONFIG_MCUBOOT_LOG_LEVEL_DBG",
    ]
    all_present = all(config.get(k) == "y" for k in required)
    details.append(
        CheckDetail(
            check_name="all_required_configs_enabled",
            passed=all_present,
            expected="BOOTLOADER_MCUBOOT, LOG, BOOT_BANNER, MCUBOOT_LOG_LEVEL_DBG all =y",
            actual=str({k: config.get(k, "missing") for k in required}),
            check_type="exact_match",
        )
    )

    # Signing type mutual exclusion — RSA vs ECDSA_P256
    # (LLM failure: setting both RSA and ECDSA signature types simultaneously)
    sig_rsa = config.get("CONFIG_BOOT_SIGNATURE_TYPE_RSA") == "y"
    sig_ec256 = config.get("CONFIG_BOOT_SIGNATURE_TYPE_ECDSA_P256") == "y"
    sig_ed25519 = config.get("CONFIG_BOOT_SIGNATURE_TYPE_ED25519") == "y"
    sig_types_set = sum([sig_rsa, sig_ec256, sig_ed25519])
    no_sig_conflict = sig_types_set <= 1
    details.append(
        CheckDetail(
            check_name="signature_type_mutual_exclusion",
            passed=no_sig_conflict,
            expected="Only one signature type (RSA, ECDSA_P256, or ED25519) may be set",
            actual="no conflict" if no_sig_conflict else f"CONFLICT: {sig_types_set} signature types set simultaneously",
            check_type="constraint",
        )
    )

    # UPGRADE_ONLY + SWAP_USING_MOVE conflict
    has_upgrade_only = config.get("CONFIG_BOOT_UPGRADE_ONLY") == "y"
    has_swap_move = config.get("CONFIG_BOOT_SWAP_USING_MOVE") == "y"
    no_swap_conflict = not (has_upgrade_only and has_swap_move)
    details.append(
        CheckDetail(
            check_name="no_upgrade_only_swap_conflict",
            passed=no_swap_conflict,
            expected="BOOT_UPGRADE_ONLY and BOOT_SWAP_USING_MOVE must not both be set",
            actual="no conflict" if no_swap_conflict else "CONFLICT: UPGRADE_ONLY + SWAP_USING_MOVE both set",
            check_type="constraint",
        )
    )

    # SINGLE_APPLICATION_SLOT + SWAP conflict
    has_single = config.get("CONFIG_SINGLE_APPLICATION_SLOT") == "y"
    has_any_swap = (
        config.get("CONFIG_BOOT_SWAP_USING_MOVE") == "y"
        or config.get("CONFIG_BOOT_SWAP_USING_SCRATCH") == "y"
    )
    no_single_swap_conflict = not (has_single and has_any_swap)
    details.append(
        CheckDetail(
            check_name="no_single_slot_swap_conflict",
            passed=no_single_swap_conflict,
            expected="SINGLE_APPLICATION_SLOT and BOOT_SWAP_* cannot both be set",
            actual="no conflict" if no_single_swap_conflict else "CONFLICT: single slot + swap both set",
            check_type="constraint",
        )
    )

    return details
