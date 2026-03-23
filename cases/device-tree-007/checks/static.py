"""Static analysis checks for Device Tree clock configuration overlay."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Device Tree clock configuration syntax and structure."""
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

    # Check 2: assigned-clocks property present
    has_assigned_clocks = "assigned-clocks" in generated_code
    details.append(
        CheckDetail(
            check_name="assigned_clocks_present",
            passed=has_assigned_clocks,
            expected="assigned-clocks property present",
            actual="present" if has_assigned_clocks else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: assigned-clock-rates property present
    has_clock_rates = "assigned-clock-rates" in generated_code
    details.append(
        CheckDetail(
            check_name="assigned_clock_rates_present",
            passed=has_clock_rates,
            expected="assigned-clock-rates property present",
            actual="present" if has_clock_rates else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: status property present
    has_status = 'status = "' in generated_code
    details.append(
        CheckDetail(
            check_name="status_present",
            passed=has_status,
            expected='status = "..." property',
            actual="present" if has_status else "missing",
            check_type="exact_match",
        )
    )

    return details
