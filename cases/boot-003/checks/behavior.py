"""Behavioral checks for Secure Boot with Signing Kconfig."""

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
    """Validate secure boot Kconfig behavioral properties."""
    details: list[CheckDetail] = []
    config = _parse_config(generated_code)

    # Check 1: signature type specified (insecure without it)
    has_sig_type = config.get("CONFIG_BOOT_SIGNATURE_TYPE_RSA") == "y" or any(
        k.startswith("CONFIG_BOOT_SIGNATURE_TYPE_") and v == "y"
        for k, v in config.items()
    )
    details.append(
        CheckDetail(
            check_name="signature_type_set",
            passed=has_sig_type,
            expected="CONFIG_BOOT_SIGNATURE_TYPE_* set (e.g. RSA)",
            actual="present" if has_sig_type else "missing (insecure!)",
            check_type="constraint",
        )
    )

    # Check 2: key file specified
    key_file = config.get("CONFIG_BOOT_SIGNATURE_KEY_FILE", "")
    has_key_file = bool(key_file.strip('"').strip())
    details.append(
        CheckDetail(
            check_name="key_file_specified",
            passed=has_key_file,
            expected="CONFIG_BOOT_SIGNATURE_KEY_FILE=<path> non-empty",
            actual=f"value={key_file!r}" if key_file else "missing",
            check_type="constraint",
        )
    )

    # Check 3: slot0 validation enabled
    validate_slot0 = config.get("CONFIG_BOOT_VALIDATE_SLOT0") == "y"
    details.append(
        CheckDetail(
            check_name="validate_slot0_enabled",
            passed=validate_slot0,
            expected="CONFIG_BOOT_VALIDATE_SLOT0=y (secure: validate primary slot)",
            actual="enabled" if validate_slot0 else "disabled or missing (insecure!)",
            check_type="constraint",
        )
    )

    # Check 4: MCUboot enabled (required for signing)
    mcuboot_ok = config.get("CONFIG_BOOTLOADER_MCUBOOT") == "y"
    details.append(
        CheckDetail(
            check_name="mcuboot_enabled",
            passed=mcuboot_ok,
            expected="CONFIG_BOOTLOADER_MCUBOOT=y",
            actual="present" if mcuboot_ok else "missing",
            check_type="constraint",
        )
    )

    # Check 5: FLASH enabled (required for secure boot image storage)
    flash_ok = config.get("CONFIG_FLASH") == "y"
    details.append(
        CheckDetail(
            check_name="flash_enabled",
            passed=flash_ok,
            expected="CONFIG_FLASH=y for image storage",
            actual="present" if flash_ok else "missing",
            check_type="constraint",
        )
    )

    # Check 6: Signing type mutual exclusion — RSA vs ECDSA_P256
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

    # Check 7: UPGRADE_ONLY + SWAP_USING_MOVE conflict
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

    # Check 8: SINGLE_APPLICATION_SLOT + SWAP conflict
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

    # Check 9: At least one signature type configured — Factor E8 Bootloader sequence
    sig_types = [
        "CONFIG_BOOT_SIGNATURE_TYPE_RSA",
        "CONFIG_BOOT_SIGNATURE_TYPE_ECDSA_P256",
        "CONFIG_BOOT_SIGNATURE_TYPE_ED25519",
    ]
    has_sig = any(s in generated_code for s in sig_types)
    details.append(CheckDetail(
        check_name="signature_type_present",
        passed=has_sig,
        expected="At least one boot signature type configured",
        actual="signature type found" if has_sig else "no signature type — unsigned images",
        check_type="constraint",
    ))

    return details
