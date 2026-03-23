"""Behavioral checks for Dual-bank Boot with External Flash Kconfig fragment."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate dual-bank external flash MCUboot Kconfig dependency chains and conflict invariants."""
    details: list[CheckDetail] = []
    config: dict[str, str] = {}
    for line in generated_code.strip().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            config[key.strip()] = val.strip()

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

    return details
