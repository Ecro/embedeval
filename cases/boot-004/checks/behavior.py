"""Behavioral checks for MCUboot Swap with Revert Kconfig."""

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
    """Validate MCUboot swap-revert Kconfig behavioral properties."""
    details: list[CheckDetail] = []
    config = _parse_config(generated_code)

    # Check 1: SWAP_USING_MOVE and UPGRADE_ONLY conflict check
    has_swap = config.get("CONFIG_BOOT_SWAP_USING_MOVE") == "y"
    has_upgrade_only = config.get("CONFIG_BOOT_UPGRADE_ONLY") == "y"
    no_conflict = not (has_swap and has_upgrade_only)
    details.append(
        CheckDetail(
            check_name="no_swap_upgrade_only_conflict",
            passed=no_conflict,
            expected="SWAP_USING_MOVE and UPGRADE_ONLY must not both be set",
            actual="no conflict" if no_conflict else "CONFLICT: both set!",
            check_type="constraint",
        )
    )

    # Check 2: SWAP_USING_MOVE enabled
    details.append(
        CheckDetail(
            check_name="swap_using_move_enabled",
            passed=has_swap,
            expected="CONFIG_BOOT_SWAP_USING_MOVE=y",
            actual="present" if has_swap else "missing",
            check_type="constraint",
        )
    )

    # Check 3: MAX_IMG_SECTORS >= 128
    sectors_val = config.get("CONFIG_BOOT_MAX_IMG_SECTORS", "")
    sectors_ok = sectors_val.isdigit() and int(sectors_val) >= 128
    details.append(
        CheckDetail(
            check_name="max_img_sectors_sufficient",
            passed=sectors_ok,
            expected="CONFIG_BOOT_MAX_IMG_SECTORS >= 128",
            actual=f"CONFIG_BOOT_MAX_IMG_SECTORS={sectors_val!r}",
            check_type="constraint",
        )
    )

    # Check 4: SINGLE_APPLICATION_SLOT absent (requires dual slot)
    no_single = config.get("CONFIG_SINGLE_APPLICATION_SLOT") != "y"
    details.append(
        CheckDetail(
            check_name="no_single_application_slot",
            passed=no_single,
            expected="CONFIG_SINGLE_APPLICATION_SLOT not set (dual-slot required for swap)",
            actual="not set" if no_single else "set (breaks swap!)",
            check_type="constraint",
        )
    )

    # Check 5: FLASH enabled
    flash_ok = config.get("CONFIG_FLASH") == "y"
    details.append(
        CheckDetail(
            check_name="flash_enabled",
            passed=flash_ok,
            expected="CONFIG_FLASH=y for swap operations",
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

    # Check 7: SINGLE_APPLICATION_SLOT + any SWAP conflict (belt-and-suspenders)
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
