"""Static analysis checks for multi-peripheral board Device Tree overlay."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate multi-peripheral overlay syntax and structure."""
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

    # Check 2: Multiple compatible strings (i2c sensor + spi flash + optional others)
    compatible_count = generated_code.count('compatible = "')
    has_multiple_compatibles = compatible_count >= 2
    details.append(
        CheckDetail(
            check_name="multiple_compatible_strings",
            passed=has_multiple_compatibles,
            expected="At least 2 compatible = \"...\" properties (sensor + flash)",
            actual=f"{compatible_count} compatible properties found",
            check_type="constraint",
        )
    )

    # Check 3: All three bus nodes referenced
    has_i2c0 = "i2c0" in generated_code
    has_spi0 = "spi0" in generated_code
    has_gpio0 = "gpio0" in generated_code
    all_buses = has_i2c0 and has_spi0 and has_gpio0
    details.append(
        CheckDetail(
            check_name="all_three_buses_present",
            passed=all_buses,
            expected="i2c0, spi0, and gpio0 all referenced",
            actual=f"i2c0={'yes' if has_i2c0 else 'no'}, spi0={'yes' if has_spi0 else 'no'}, gpio0={'yes' if has_gpio0 else 'no'}",
            check_type="constraint",
        )
    )

    # Check 4: status property appears multiple times (parent nodes must also be enabled)
    status_okay_count = generated_code.count('status = "okay"')
    has_multiple_status = status_okay_count >= 3
    details.append(
        CheckDetail(
            check_name="multiple_status_okay",
            passed=has_multiple_status,
            expected="At least 3 status = \"okay\" entries (one per bus + child nodes)",
            actual=f"{status_okay_count} status = \"okay\" entries found",
            check_type="constraint",
        )
    )

    # Check 5: Sufficient nesting depth (many peripheral nodes)
    has_deep_nesting = open_count >= 6
    details.append(
        CheckDetail(
            check_name="sufficient_node_count",
            passed=has_deep_nesting,
            expected="At least 6 opening braces (3 buses + 3 child nodes minimum)",
            actual=f"{open_count} opening braces found",
            check_type="constraint",
        )
    )

    return details
