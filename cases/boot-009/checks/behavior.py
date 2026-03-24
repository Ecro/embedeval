"""Behavioral checks for Dual-bank Boot with External Flash Kconfig fragment."""

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
    """Validate dual-bank external flash MCUboot Kconfig dependency chains and conflict invariants."""
    details: list[CheckDetail] = []
    config = _parse_config(generated_code)

    ext_flash_secondary_enabled = config.get("CONFIG_PM_EXTERNAL_FLASH_MCUBOOT_SECONDARY") == "y"
    spi_nor_enabled = config.get("CONFIG_SPI_NOR") == "y"
    flash_enabled = config.get("CONFIG_FLASH") == "y"
    flash_map_enabled = config.get("CONFIG_FLASH_MAP") == "y"
    stream_flash_enabled = config.get("CONFIG_STREAM_FLASH") == "y"
    single_slot_enabled = config.get("CONFIG_SINGLE_APPLICATION_SLOT") == "y"
    page_size_val = config.get("CONFIG_SPI_NOR_FLASH_LAYOUT_PAGE_SIZE", "")

    # Metamorphic: PM_EXTERNAL_FLASH_MCUBOOT_SECONDARY requires SPI_NOR=y
    ext_flash_needs_spi_nor = not (ext_flash_secondary_enabled and not spi_nor_enabled)
    details.append(
        CheckDetail(
            check_name="ext_flash_secondary_requires_spi_nor",
            passed=ext_flash_needs_spi_nor,
            expected="PM_EXTERNAL_FLASH_MCUBOOT_SECONDARY requires SPI_NOR=y",
            actual=(
                f"SPI_NOR={config.get('CONFIG_SPI_NOR', 'n')}, "
                f"PM_EXTERNAL_FLASH_MCUBOOT_SECONDARY={config.get('CONFIG_PM_EXTERNAL_FLASH_MCUBOOT_SECONDARY', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Metamorphic: SPI_NOR requires FLASH=y
    spi_nor_needs_flash = not (spi_nor_enabled and not flash_enabled)
    details.append(
        CheckDetail(
            check_name="spi_nor_requires_flash",
            passed=spi_nor_needs_flash,
            expected="SPI_NOR requires FLASH=y",
            actual=(
                f"FLASH={config.get('CONFIG_FLASH', 'n')}, "
                f"SPI_NOR={config.get('CONFIG_SPI_NOR', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Behavioral: page size should be 4096 (standard NOR flash erase size)
    page_size_ok = page_size_val == "4096"
    details.append(
        CheckDetail(
            check_name="spi_nor_page_size_correct",
            passed=page_size_ok,
            expected="CONFIG_SPI_NOR_FLASH_LAYOUT_PAGE_SIZE=4096",
            actual=f"SPI_NOR_FLASH_LAYOUT_PAGE_SIZE={page_size_val!r}",
            check_type="constraint",
        )
    )

    # Conflict: SINGLE_APPLICATION_SLOT incompatible with dual-bank external flash
    no_single_slot = not single_slot_enabled
    details.append(
        CheckDetail(
            check_name="no_single_application_slot_conflict",
            passed=no_single_slot,
            expected="CONFIG_SINGLE_APPLICATION_SLOT=y absent (incompatible with dual-bank)",
            actual=(
                "not set"
                if no_single_slot
                else "CONFIG_SINGLE_APPLICATION_SLOT=y set (conflicts with dual-bank external flash)"
            ),
            check_type="constraint",
        )
    )

    # Summary: all required configs present
    required = [
        "CONFIG_FLASH",
        "CONFIG_SPI_NOR",
        "CONFIG_PM_EXTERNAL_FLASH_MCUBOOT_SECONDARY",
    ]
    all_present = all(config.get(k) == "y" for k in required)
    details.append(
        CheckDetail(
            check_name="all_required_configs_enabled",
            passed=all_present,
            expected="FLASH, SPI_NOR, PM_EXTERNAL_FLASH_MCUBOOT_SECONDARY all =y",
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

    return details
