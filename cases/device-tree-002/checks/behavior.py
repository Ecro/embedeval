"""Behavioral checks for SPI NOR flash Device Tree overlay."""

from embedeval.models import CheckDetail

_FAKE_DT_PROPERTIES = [
    "pin-config",
    "mux-config",
    "clock-speed",
]


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate SPI NOR flash overlay behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: No fake DT properties
    found_fake = [prop for prop in _FAKE_DT_PROPERTIES if prop in generated_code]
    details.append(
        CheckDetail(
            check_name="no_fake_dt_properties",
            passed=not found_fake,
            expected="No hallucinated DT properties (pin-config, mux-config, clock-speed)",
            actual="clean" if not found_fake else f"fake properties found: {found_fake}",
            check_type="hallucination",
        )
    )

    # Check 2: Parent SPI bus must be "okay" (LLM failure: enables child but not parent)
    # Check for spi0 with status okay
    has_spi0_okay = (
        "&spi0" in generated_code
        and 'status = "okay"' in generated_code
    )
    details.append(
        CheckDetail(
            check_name="spi0_parent_enabled",
            passed=has_spi0_okay,
            expected="&spi0 present with status = \"okay\"",
            actual="present" if has_spi0_okay else "missing — parent SPI bus not enabled",
            check_type="constraint",
        )
    )

    # Check 3: Correct compatible string (AI failure: wrong vendor prefix or misspelling)
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

    # Check 4: reg = <0> for chip select 0 (AI failure: uses address like 0x00 or omits reg)
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

    # Check 5: spi-max-frequency = <1000000> (AI failure: omits or uses wrong value)
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

    # Check 6: size = <0x100000> for 1MB (AI failure: uses decimal or wrong size)
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

    # Check 7: status = "okay" present
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

    # Check 8: Flash node uses @address format (e.g. w25q128@0)
    # LLM failure: names node flash { instead of flash@0 {
    import re
    has_at_addr = bool(re.search(r"\w+@0\s*\{", generated_code))
    details.append(
        CheckDetail(
            check_name="flash_node_at_address_format",
            passed=has_at_addr,
            expected="SPI flash node uses @0 address suffix (e.g. w25q128@0)",
            actual="present" if has_at_addr else "missing — node name should include @address",
            check_type="constraint",
        )
    )

    return details
