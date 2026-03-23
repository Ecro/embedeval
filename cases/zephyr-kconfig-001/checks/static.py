"""Static analysis checks for Zephyr Kconfig fragments."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Kconfig fragment format and required options."""
    details: list[CheckDetail] = []
    lines = [
        line.strip()
        for line in generated_code.strip().splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    # Check 1: All lines use CONFIG_ prefix
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

    # Check 2: CONFIG_SPI=y present
    has_spi = any("CONFIG_SPI=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="spi_enabled",
            passed=has_spi,
            expected="CONFIG_SPI=y",
            actual="present" if has_spi else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: CONFIG_DMA=y present (dependency)
    has_dma = any("CONFIG_DMA=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="dma_enabled",
            passed=has_dma,
            expected="CONFIG_DMA=y",
            actual="present" if has_dma else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: CONFIG_SPI_DMA=y present
    has_spi_dma = any("CONFIG_SPI_DMA=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="spi_dma_enabled",
            passed=has_spi_dma,
            expected="CONFIG_SPI_DMA=y",
            actual="present" if has_spi_dma else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: No conflicting options
    no_conflict = not any("CONFIG_SPI_SLAVE=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="no_conflicting_options",
            passed=no_conflict,
            expected="CONFIG_SPI_SLAVE not enabled",
            actual="not present" if no_conflict else "CONFIG_SPI_SLAVE=y found",
            check_type="constraint",
        )
    )

    return details
