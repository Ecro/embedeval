"""Static analysis checks for Dual-bank Boot with External Flash Kconfig fragment."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate dual-bank external flash MCUboot Kconfig fragment format and required options."""
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
            expected="All lines: CONFIG_*=value",
            actual=f"{len(lines)} lines, valid={valid_format}",
            check_type="exact_match",
        )
    )

    # Check 2: CONFIG_PM_EXTERNAL_FLASH_MCUBOOT_SECONDARY=y present
    has_ext_flash_secondary = any(
        "CONFIG_PM_EXTERNAL_FLASH_MCUBOOT_SECONDARY=y" in line for line in lines
    )
    details.append(
        CheckDetail(
            check_name="pm_external_flash_mcuboot_secondary_enabled",
            passed=has_ext_flash_secondary,
            expected="CONFIG_PM_EXTERNAL_FLASH_MCUBOOT_SECONDARY=y",
            actual="present" if has_ext_flash_secondary else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: CONFIG_SPI_NOR=y present
    has_spi_nor = any("CONFIG_SPI_NOR=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="spi_nor_enabled",
            passed=has_spi_nor,
            expected="CONFIG_SPI_NOR=y",
            actual="present" if has_spi_nor else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: CONFIG_SPI_NOR_FLASH_LAYOUT_PAGE_SIZE=4096 present
    has_page_size = any("CONFIG_SPI_NOR_FLASH_LAYOUT_PAGE_SIZE=4096" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="spi_nor_page_size_4096",
            passed=has_page_size,
            expected="CONFIG_SPI_NOR_FLASH_LAYOUT_PAGE_SIZE=4096",
            actual="present" if has_page_size else "missing or wrong value",
            check_type="exact_match",
        )
    )

    # Check 5: CONFIG_FLASH=y present (base dependency)
    has_flash = any("CONFIG_FLASH=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="flash_enabled",
            passed=has_flash,
            expected="CONFIG_FLASH=y",
            actual="present" if has_flash else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: CONFIG_SINGLE_APPLICATION_SLOT must NOT be present
    no_single_slot = not any("CONFIG_SINGLE_APPLICATION_SLOT=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="single_application_slot_absent",
            passed=no_single_slot,
            expected="CONFIG_SINGLE_APPLICATION_SLOT=y absent (incompatible with dual-bank)",
            actual="not present" if no_single_slot else "present (conflicts with dual-bank external flash)",
            check_type="constraint",
        )
    )

    return details
