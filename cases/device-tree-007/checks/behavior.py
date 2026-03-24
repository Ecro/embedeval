"""Behavioral checks for Device Tree clock source configuration."""

import re

from embedeval.models import CheckDetail

_FAKE_DT_PROPERTIES = [
    "pin-config",
    "mux-config",
    "clock-speed",     # Should be clock-frequency; clock-speed is hallucinated
]


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Device Tree clock configuration behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: No fake DT properties — especially clock-speed (should be clock-frequency)
    found_fake = [prop for prop in _FAKE_DT_PROPERTIES if prop in generated_code]
    details.append(
        CheckDetail(
            check_name="no_fake_dt_properties",
            passed=not found_fake,
            expected="No hallucinated DT properties; clock-speed does not exist (use clock-frequency)",
            actual="clean" if not found_fake else f"fake properties found: {found_fake}",
            check_type="hallucination",
        )
    )

    # Check 2: Clock rate value is reasonable (> 0 and <= 1 GHz)
    rate_match = re.search(r"assigned-clock-rates\s*=\s*<(\d+)>", generated_code)
    if rate_match:
        rate_value = int(rate_match.group(1))
        rate_valid = 0 < rate_value <= 1_000_000_000
    else:
        rate_value = 0
        rate_valid = False
    details.append(
        CheckDetail(
            check_name="clock_rate_value_reasonable",
            passed=rate_valid,
            expected="Clock rate > 0 and <= 1000000000 (1 GHz)",
            actual=f"rate={rate_value}" if rate_match else "no rate value found",
            check_type="constraint",
        )
    )

    # Check 3: assigned-clocks references a phandle (valid clock source)
    has_clock_ref = bool(re.search(r"assigned-clocks\s*=\s*<&", generated_code))
    details.append(
        CheckDetail(
            check_name="assigned_clocks_valid_reference",
            passed=has_clock_ref,
            expected="assigned-clocks references a phandle (e.g. <&rcc ...>)",
            actual="present" if has_clock_ref else "missing or invalid clock reference",
            check_type="constraint",
        )
    )

    # Check 4: status = "okay"
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

    # Check 5: No clock_rate = 0 (zero rate is invalid)
    has_zero_rate = bool(re.search(r"assigned-clock-rates\s*=\s*<0>", generated_code))
    details.append(
        CheckDetail(
            check_name="clock_rate_not_zero",
            passed=not has_zero_rate,
            expected="Clock rate must not be 0",
            actual="valid" if not has_zero_rate else "clock rate is 0 - invalid configuration",
            check_type="constraint",
        )
    )

    # Check 6: No plain integer clock rate without phandle in assigned-clocks (hallucination guard)
    # Fake pattern: assigned-clocks = <16000000>; instead of a phandle reference
    has_fake_direct_freq = bool(
        re.search(r"assigned-clocks\s*=\s*<\d+>", generated_code)
    )
    details.append(
        CheckDetail(
            check_name="no_frequency_in_assigned_clocks",
            passed=not has_fake_direct_freq,
            expected="assigned-clocks must contain phandle, not raw frequency",
            actual="clean" if not has_fake_direct_freq else "raw frequency in assigned-clocks (wrong - use phandle)",
            check_type="hallucination",
        )
    )

    # Check 7: uart0 (or relevant peripheral) referenced
    has_peripheral_node = (
        "&uart0" in generated_code
        or "&usart1" in generated_code
        or "&uart" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="peripheral_node_referenced",
            passed=has_peripheral_node,
            expected="Peripheral node (e.g. &uart0) referenced for clock assignment",
            actual="present" if has_peripheral_node else "missing peripheral node reference",
            check_type="constraint",
        )
    )

    # Check 8: assigned-clock-rates present (not just assigned-clocks alone)
    has_clock_rates = "assigned-clock-rates" in generated_code
    details.append(
        CheckDetail(
            check_name="assigned_clock_rates_present",
            passed=has_clock_rates,
            expected="assigned-clock-rates property present alongside assigned-clocks",
            actual="present" if has_clock_rates else "missing — clock rate not set",
            check_type="constraint",
        )
    )

    return details
