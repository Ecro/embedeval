"""Behavioral checks for MCUboot Downgrade Protection Kconfig fragment."""

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
    """Validate MCUboot downgrade protection Kconfig dependency chains and invariants."""
    details: list[CheckDetail] = []
    config = _parse_config(generated_code)

    mcuboot_enabled = config.get("CONFIG_BOOTLOADER_MCUBOOT") == "y"
    build_num_cmp_enabled = config.get("CONFIG_BOOT_VERSION_CMP_USE_BUILD_NUMBER") == "y"
    validate_slot0_enabled = config.get("CONFIG_BOOT_VALIDATE_SLOT0") == "y"
    upgrade_only_enabled = config.get("CONFIG_BOOT_UPGRADE_ONLY") == "y"
    single_slot_enabled = config.get("CONFIG_SINGLE_APPLICATION_SLOT") == "y"

    # Metamorphic: BOOT_VERSION_CMP_USE_BUILD_NUMBER is meaningful only with MCUboot
    build_num_needs_mcuboot = not (build_num_cmp_enabled and not mcuboot_enabled)
    details.append(
        CheckDetail(
            check_name="build_num_cmp_requires_mcuboot",
            passed=build_num_needs_mcuboot,
            expected="BOOT_VERSION_CMP_USE_BUILD_NUMBER requires BOOTLOADER_MCUBOOT=y",
            actual=(
                f"BOOTLOADER_MCUBOOT={config.get('CONFIG_BOOTLOADER_MCUBOOT', 'n')}, "
                f"BOOT_VERSION_CMP_USE_BUILD_NUMBER={config.get('CONFIG_BOOT_VERSION_CMP_USE_BUILD_NUMBER', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Behavioral: downgrade protection requires slot0 validation
    downgrade_needs_validate = not (build_num_cmp_enabled and not validate_slot0_enabled)
    details.append(
        CheckDetail(
            check_name="downgrade_protection_requires_slot0_validation",
            passed=downgrade_needs_validate,
            expected="BOOT_VERSION_CMP_USE_BUILD_NUMBER requires BOOT_VALIDATE_SLOT0=y",
            actual=(
                f"BOOT_VALIDATE_SLOT0={config.get('CONFIG_BOOT_VALIDATE_SLOT0', 'n')}, "
                f"BOOT_VERSION_CMP_USE_BUILD_NUMBER={config.get('CONFIG_BOOT_VERSION_CMP_USE_BUILD_NUMBER', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Constraint: SINGLE_APPLICATION_SLOT incompatible with upgrade protection
    no_single_slot = not single_slot_enabled
    details.append(
        CheckDetail(
            check_name="single_application_slot_absent",
            passed=no_single_slot,
            expected="CONFIG_SINGLE_APPLICATION_SLOT=y absent (incompatible with downgrade protection)",
            actual=(
                "not set"
                if no_single_slot
                else "CONFIG_SINGLE_APPLICATION_SLOT=y set (conflicts with downgrade protection)"
            ),
            check_type="constraint",
        )
    )

    # Summary: all required configs present
    required = [
        "CONFIG_BOOTLOADER_MCUBOOT",
        "CONFIG_BOOT_VALIDATE_SLOT0",
        "CONFIG_BOOT_VERSION_CMP_USE_BUILD_NUMBER",
    ]
    all_present = all(config.get(k) == "y" for k in required)
    details.append(
        CheckDetail(
            check_name="all_required_configs_enabled",
            passed=all_present,
            expected="BOOTLOADER_MCUBOOT, BOOT_VALIDATE_SLOT0, BOOT_VERSION_CMP_USE_BUILD_NUMBER all =y",
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
