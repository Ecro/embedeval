"""Behavioral checks for Multi-image Boot Configuration Kconfig."""

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
    """Validate multi-image boot Kconfig behavioral properties."""
    details: list[CheckDetail] = []
    config = _parse_config(generated_code)

    # Check 1: BOOT_IMAGE_NUMBER and UPDATEABLE_IMAGE_NUMBER are consistent
    image_num = config.get("CONFIG_BOOT_IMAGE_NUMBER", "")
    updateable_num = config.get("CONFIG_UPDATEABLE_IMAGE_NUMBER", "")
    both_present = bool(image_num) and bool(updateable_num)
    consistent = image_num == updateable_num and both_present
    details.append(
        CheckDetail(
            check_name="image_numbers_consistent",
            passed=consistent,
            expected="BOOT_IMAGE_NUMBER == UPDATEABLE_IMAGE_NUMBER (both 2)",
            actual=f"BOOT_IMAGE_NUMBER={image_num}, UPDATEABLE_IMAGE_NUMBER={updateable_num}",
            check_type="constraint",
        )
    )

    # Check 2: BOOT_IMAGE_NUMBER=2 (dual-core)
    image_num_ok = image_num == "2"
    details.append(
        CheckDetail(
            check_name="boot_image_number_2",
            passed=image_num_ok,
            expected="CONFIG_BOOT_IMAGE_NUMBER=2",
            actual=f"CONFIG_BOOT_IMAGE_NUMBER={image_num!r}",
            check_type="constraint",
        )
    )

    # Check 3: PCD_APP enabled for network core
    pcd_ok = config.get("CONFIG_PCD_APP") == "y"
    details.append(
        CheckDetail(
            check_name="pcd_app_enabled",
            passed=pcd_ok,
            expected="CONFIG_PCD_APP=y for network core update support",
            actual="present" if pcd_ok else "missing (network core updates won't work)",
            check_type="constraint",
        )
    )

    # Check 4: SINGLE_APPLICATION_SLOT absent
    no_single = config.get("CONFIG_SINGLE_APPLICATION_SLOT") != "y"
    details.append(
        CheckDetail(
            check_name="no_single_application_slot",
            passed=no_single,
            expected="CONFIG_SINGLE_APPLICATION_SLOT not set (incompatible with multi-image)",
            actual="not set" if no_single else "set (conflicts with multi-image!)",
            check_type="constraint",
        )
    )

    # Check 5: MCUboot enabled
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

    return details
