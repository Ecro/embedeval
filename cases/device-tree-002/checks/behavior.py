"""Behavioral checks for SPI NOR flash Device Tree overlay."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate SPI NOR flash overlay behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: Correct compatible string (AI failure: wrong vendor prefix or misspelling)
    has_jedec_spi_nor = 'compatible = "jedec,spi-nor"' in generated_code
    details.append(
        CheckDetail(
            check_name="jedec_spi_nor_compatible",
            passed=has_jedec_spi_nor,
            expected='compatible = "jedec,spi-nor"',
            actual="present" if has_jedec_spi_nor else "missing or wrong compatible string",
            check_type="exact_match",
        )
    )

    # Check 2: reg = <0> for chip select 0 (AI failure: uses address like 0x00 or omits reg)
    has_reg_0 = "reg = <0>" in generated_code
    details.append(
        CheckDetail(
            check_name="reg_chip_select_0",
            passed=has_reg_0,
            expected="reg = <0>",
            actual="present" if has_reg_0 else "missing or wrong chip select value",
            check_type="exact_match",
        )
    )

    # Check 3: spi-max-frequency = <1000000> (AI failure: omits or uses wrong value)
    has_freq_1mhz = "spi-max-frequency = <1000000>" in generated_code
    details.append(
        CheckDetail(
            check_name="spi_max_frequency_1mhz",
            passed=has_freq_1mhz,
            expected="spi-max-frequency = <1000000>",
            actual="present" if has_freq_1mhz else "missing or wrong frequency",
            check_type="exact_match",
        )
    )

    # Check 4: size = <0x100000> for 1MB (AI failure: uses decimal or wrong size)
    has_size_1mb = "size = <0x100000>" in generated_code
    details.append(
        CheckDetail(
            check_name="size_1mb",
            passed=has_size_1mb,
            expected="size = <0x100000>",
            actual="present" if has_size_1mb else "missing or wrong size value",
            check_type="exact_match",
        )
    )

    # Check 5: status = "okay" present
    has_status_okay = 'status = "okay"' in generated_code
    details.append(
        CheckDetail(
            check_name="status_okay",
            passed=has_status_okay,
            expected='status = "okay"',
            actual="present" if has_status_okay else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: Flash node is a child of spi0 (AI failure: places at root or wrong bus)
    has_spi0_parent = "&spi0" in generated_code
    details.append(
        CheckDetail(
            check_name="spi0_bus_parent",
            passed=has_spi0_parent,
            expected="Node under &spi0 bus",
            actual="&spi0 referenced" if has_spi0_parent else "&spi0 not found",
            check_type="constraint",
        )
    )

    return details
