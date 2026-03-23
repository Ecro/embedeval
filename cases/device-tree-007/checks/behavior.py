"""Behavioral checks for Device Tree clock source configuration."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Device Tree clock configuration behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: Clock rate value is reasonable (> 0 and <= 1 GHz)
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

    # Check 2: assigned-clocks references a phandle (valid clock source)
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

    # Check 3: status = "okay"
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

    # Check 4: No clock_rate = 0 (zero rate is invalid)
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

    # Check 5: No plain integer clock rate without phandle in assigned-clocks (hallucination guard)
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

    return details
