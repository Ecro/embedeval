"""Static analysis checks for Device Tree regulator node overlay."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Device Tree regulator node syntax and structure."""
    details: list[CheckDetail] = []

    # Check 1: Braces balanced
    open_count = generated_code.count("{")
    close_count = generated_code.count("}")
    braces_match = open_count == close_count and open_count > 0
    details.append(
        CheckDetail(
            check_name="braces_balanced",
            passed=braces_match,
            expected="Matching opening/closing braces",
            actual=f"open={open_count}, close={close_count}",
            check_type="syntax",
        )
    )

    # Check 2: compatible = "regulator-fixed" present
    has_compatible = 'compatible = "regulator-fixed"' in generated_code
    details.append(
        CheckDetail(
            check_name="regulator_fixed_compatible",
            passed=has_compatible,
            expected='compatible = "regulator-fixed"',
            actual="present" if has_compatible else "missing or wrong compatible",
            check_type="exact_match",
        )
    )

    # Check 3: regulator-min-microvolt present
    has_min = "regulator-min-microvolt" in generated_code
    details.append(
        CheckDetail(
            check_name="regulator_min_microvolt_present",
            passed=has_min,
            expected="regulator-min-microvolt property present",
            actual="present" if has_min else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: regulator-max-microvolt present
    has_max = "regulator-max-microvolt" in generated_code
    details.append(
        CheckDetail(
            check_name="regulator_max_microvolt_present",
            passed=has_max,
            expected="regulator-max-microvolt property present",
            actual="present" if has_max else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: regulator-boot-on present
    has_boot_on = "regulator-boot-on" in generated_code
    details.append(
        CheckDetail(
            check_name="regulator_boot_on_present",
            passed=has_boot_on,
            expected="regulator-boot-on property present",
            actual="present" if has_boot_on else "missing",
            check_type="exact_match",
        )
    )

    return details
