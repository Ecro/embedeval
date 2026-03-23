"""Static analysis checks for PWM LED Device Tree overlay."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate PWM LED overlay syntax and structure."""
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

    # Check 3: pwms property present (AI commonly omits or misspells this)
    has_pwms = "pwms = <" in generated_code
    details.append(
        CheckDetail(
            check_name="pwms_property_present",
            passed=has_pwms,
            expected="pwms = <...> property",
            actual="present" if has_pwms else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: label property present
    has_label = "label = " in generated_code
    details.append(
        CheckDetail(
            check_name="label_property_present",
            passed=has_label,
            expected="label property",
            actual="present" if has_label else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: At least two nested brace levels (parent pwm-leds node + child LED node)
    # A minimal correct overlay has at least 3 opening braces: root/parent, pwm-leds, child
    has_nested_nodes = open_count >= 2
    details.append(
        CheckDetail(
            check_name="nested_node_structure",
            passed=has_nested_nodes,
            expected="At least 2 brace levels (parent + child node)",
            actual=f"{open_count} opening braces found",
            check_type="constraint",
        )
    )

    return details
