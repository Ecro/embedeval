"""Static analysis checks for CAN bus controller Device Tree overlay."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate CAN bus controller overlay syntax and structure."""
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

    # Check 3: status property present
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

    # Check 4: bus-speed property present (AI commonly omits this)
    has_bus_speed = "bus-speed" in generated_code
    details.append(
        CheckDetail(
            check_name="bus_speed_present",
            passed=has_bus_speed,
            expected="bus-speed property",
            actual="present" if has_bus_speed else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: can0 node referenced
    has_can0 = "can0" in generated_code
    details.append(
        CheckDetail(
            check_name="can0_node_referenced",
            passed=has_can0,
            expected="can0 node reference",
            actual="present" if has_can0 else "missing",
            check_type="constraint",
        )
    )

    # Check 6: Child node present (at least 2 opening braces: can0 + child transceiver)
    has_child_node = open_count >= 2
    details.append(
        CheckDetail(
            check_name="transceiver_child_node",
            passed=has_child_node,
            expected="At least 2 brace levels (can0 + child transceiver node)",
            actual=f"{open_count} opening braces found",
            check_type="constraint",
        )
    )

    return details
