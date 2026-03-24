"""Behavioral checks for Device Tree voltage regulator node."""

import re

from embedeval.models import CheckDetail

_FAKE_DT_PROPERTIES = [
    "pin-config",
    "mux-config",
    "clock-speed",
]


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Device Tree regulator behavioral properties and domain invariants."""
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

    # Check 2: min-microvolt <= max-microvolt
    min_match = re.search(r"regulator-min-microvolt\s*=\s*<(\d+)>", generated_code)
    max_match = re.search(r"regulator-max-microvolt\s*=\s*<(\d+)>", generated_code)
    if min_match and max_match:
        min_val = int(min_match.group(1))
        max_val = int(max_match.group(1))
        min_lte_max = min_val <= max_val
    else:
        min_val = max_val = 0
        min_lte_max = False
    details.append(
        CheckDetail(
            check_name="min_voltage_lte_max_voltage",
            passed=min_lte_max,
            expected="regulator-min-microvolt <= regulator-max-microvolt",
            actual=f"min={min_val}, max={max_val}" if (min_match and max_match) else "one or both values missing",
            check_type="constraint",
        )
    )

    # Check 3: Values are in microvolts, not millivolts (millivolt range is < 30000)
    min_is_microvolt = (min_val >= 100_000) if min_match else False
    max_is_microvolt = (max_val >= 100_000) if max_match else False
    uses_microvolts = min_is_microvolt and max_is_microvolt
    details.append(
        CheckDetail(
            check_name="values_in_microvolts_not_millivolts",
            passed=uses_microvolts,
            expected="Voltage values in microvolts (>= 100000), not millivolts",
            actual=f"min={min_val}, max={max_val}" if (min_match and max_match) else "values missing",
            check_type="constraint",
        )
    )

    # Check 4: No regulator-min-millivolt or regulator-max-millivolt (wrong unit property names)
    has_millivolt_names = (
        "regulator-min-millivolt" in generated_code
        or "regulator-max-millivolt" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="no_millivolt_property_names",
            passed=not has_millivolt_names,
            expected="Use regulator-min/max-microvolt, not millivolt",
            actual="clean" if not has_millivolt_names else "millivolt property names used (wrong unit)",
            check_type="hallucination",
        )
    )

    # Check 5: status = "okay"
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

    # Check 6: regulator-name property present
    has_name = "regulator-name" in generated_code
    details.append(
        CheckDetail(
            check_name="regulator_name_present",
            passed=has_name,
            expected="regulator-name property present",
            actual="present" if has_name else "missing",
            check_type="exact_match",
        )
    )

    # Check 7: regulator-fixed compatible used (parent node required)
    # LLM failure: creates regulator node without compatible string
    has_compatible = 'compatible = "regulator-fixed"' in generated_code
    details.append(
        CheckDetail(
            check_name="regulator_fixed_compatible",
            passed=has_compatible,
            expected='compatible = "regulator-fixed"',
            actual="present" if has_compatible else "missing — regulator node needs compatible",
            check_type="exact_match",
        )
    )

    # Check 8: Voltage values are within realistic range (100mV - 5V)
    # LLM failure: sometimes generates absurd values like 33000000 (33V in microvolts)
    realistic_voltage = True
    if min_match and max_match and uses_microvolts:
        # Realistic embedded voltages: 0.8V (800000uV) to 5V (5000000uV)
        realistic_voltage = (100_000 <= min_val <= 5_500_000) and (100_000 <= max_val <= 5_500_000)
    details.append(
        CheckDetail(
            check_name="voltage_in_realistic_range",
            passed=realistic_voltage,
            expected="Voltage values between 100mV (100000uV) and 5.5V (5500000uV)",
            actual=f"min={min_val}uV, max={max_val}uV" if (min_match and max_match) else "values missing",
            check_type="constraint",
        )
    )

    return details
