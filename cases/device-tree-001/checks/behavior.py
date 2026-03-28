"""Behavioral checks for Device Tree I2C sensor overlay."""

import re

from embedeval.models import CheckDetail

# Fake DT properties that LLMs commonly invent
_FAKE_DT_PROPERTIES = [
    "pin-config",      # Should be pinctrl-0
    "mux-config",      # Does not exist
    "clock-speed",     # Should be clock-frequency
]


def _check_semicolons(generated_code: str) -> tuple[bool, str]:
    """Check that every property line ends with semicolon."""
    # Property lines: lines containing '=' that are not node openers
    property_lines = []
    for line in generated_code.splitlines():
        stripped = line.strip()
        # Skip blank, comment, node open/close, and include lines
        if not stripped or stripped.startswith("//") or stripped.startswith("/*"):
            continue
        if stripped.endswith("{") or stripped == "}" or stripped == "};":
            continue
        if stripped.startswith("#include") or stripped.startswith("/"):
            continue
        # This looks like a property line
        if "=" in stripped or (stripped and not stripped.startswith("&") and not stripped.endswith("{")):
            # Property lines should end with ;
            if "=" in stripped and not stripped.endswith(";") and not stripped.endswith(","):
                property_lines.append(stripped[:40])
    return len(property_lines) == 0, property_lines[:3]


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Device Tree overlay behavioral properties."""
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

    # Check 2: No clock-speed (should be clock-frequency)
    has_clock_speed = "clock-speed" in generated_code
    details.append(
        CheckDetail(
            check_name="no_clock_speed_property",
            passed=not has_clock_speed,
            expected="Use clock-frequency not clock-speed (clock-speed is hallucinated)",
            actual="clean" if not has_clock_speed else "clock-speed found (non-existent property)",
            check_type="hallucination",
        )
    )

    # Check 3: Sensor node with correct compatible
    has_bme280 = 'compatible = "bosch,bme280"' in generated_code
    details.append(
        CheckDetail(
            check_name="sensor_compatible",
            passed=has_bme280,
            expected='compatible = "bosch,bme280"',
            actual="present" if has_bme280 else "missing or wrong",
            check_type="exact_match",
        )
    )

    # Check 4: reg matches 0x76
    has_reg_76 = "reg = <0x76>" in generated_code
    details.append(
        CheckDetail(
            check_name="reg_address_0x76",
            passed=has_reg_76,
            expected="reg = <0x76>",
            actual="present" if has_reg_76 else "missing or wrong",
            check_type="exact_match",
        )
    )

    # Check 5: GPIO interrupt connected (int-gpios present)
    has_int_gpios = "int-gpios" in generated_code
    details.append(
        CheckDetail(
            check_name="interrupt_gpio_present",
            passed=has_int_gpios,
            expected="int-gpios property present",
            actual="present" if has_int_gpios else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: GPIO active low polarity
    has_active_low = "GPIO_ACTIVE_LOW" in generated_code
    details.append(
        CheckDetail(
            check_name="gpio_active_low",
            passed=has_active_low,
            expected="GPIO_ACTIVE_LOW polarity",
            actual="present" if has_active_low else "missing",
            check_type="exact_match",
        )
    )

    # Check 7: status = "okay"
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

    # Check 8: Node is child of i2c bus (i2c0 reference)
    has_i2c_bus = "i2c0" in generated_code
    details.append(
        CheckDetail(
            check_name="i2c_bus_parent",
            passed=has_i2c_bus,
            expected="Node under i2c0 bus",
            actual="i2c0 referenced" if has_i2c_bus else "i2c0 not found",
            check_type="constraint",
        )
    )

    # Check 9: Node address format — sensor node uses @76 (node-name@addr format)
    # LLM failure: uses bme280 { instead of bme280@76 {
    has_at_addr = "bme280@76" in generated_code or "bme280@0x76" in generated_code
    details.append(
        CheckDetail(
            check_name="node_at_address_format",
            passed=has_at_addr,
            expected="Node name uses @76 address suffix (e.g. bme280@76)",
            actual="present" if has_at_addr else "missing — node name should include @address",
            check_type="constraint",
        )
    )

    # Check 10: compatible string format (vendor,device) — Factor A11 Device Tree
    has_compatible = bool(re.search(r'compatible\s*=\s*"[a-z]+,[a-z]', generated_code))
    details.append(CheckDetail(
        check_name="compatible_string_valid",
        passed=has_compatible,
        expected='compatible = "vendor,device" format',
        actual="valid format" if has_compatible else "missing or invalid compatible string",
        check_type="constraint",
    ))

    # Check 11: status = "okay" on active node — Factor A11 Device Tree
    has_status = bool(re.search(r'status\s*=\s*"okay"', generated_code))
    details.append(CheckDetail(
        check_name="status_okay_present",
        passed=has_status,
        expected='status = "okay" on active device node',
        actual="present" if has_status else "missing status = okay",
        check_type="constraint",
    ))

    return details
