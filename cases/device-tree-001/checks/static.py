"""Static analysis checks for Device Tree overlays."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Device Tree overlay syntax and structure."""
    details: list[CheckDetail] = []

    # Check 1: Braces match (opening/closing)
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

    # Check 2: compatible string present and in correct format
    has_compatible = 'compatible = "' in generated_code
    details.append(
        CheckDetail(
            check_name="compatible_present",
            passed=has_compatible,
            expected='compatible = "..." property',
            actual="present" if has_compatible else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: reg property present
    has_reg = "reg = <" in generated_code
    details.append(
        CheckDetail(
            check_name="reg_property_present",
            passed=has_reg,
            expected="reg = <...> property",
            actual="present" if has_reg else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: status property present
    has_status = 'status = "' in generated_code
    details.append(
        CheckDetail(
            check_name="status_property_present",
            passed=has_status,
            expected='status = "..." property',
            actual="present" if has_status else "missing",
            check_type="exact_match",
        )
    )

    return details
