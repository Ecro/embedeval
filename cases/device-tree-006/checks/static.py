"""Static analysis checks for Device Tree pinctrl overlay."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Device Tree pinctrl overlay syntax and structure."""
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

    # Check 2: uart0 node referenced
    has_uart0 = "&uart0" in generated_code
    details.append(
        CheckDetail(
            check_name="uart0_node_referenced",
            passed=has_uart0,
            expected="&uart0 node reference present",
            actual="present" if has_uart0 else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: pinctrl-names property present
    has_pinctrl_names = "pinctrl-names" in generated_code
    details.append(
        CheckDetail(
            check_name="pinctrl_names_present",
            passed=has_pinctrl_names,
            expected="pinctrl-names property present",
            actual="present" if has_pinctrl_names else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: pinctrl-0 property present
    has_pinctrl_0 = "pinctrl-0" in generated_code
    details.append(
        CheckDetail(
            check_name="pinctrl_0_present",
            passed=has_pinctrl_0,
            expected="pinctrl-0 property present",
            actual="present" if has_pinctrl_0 else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: No fake pin-config or mux-config properties (hallucination guards)
    has_fake_pin_config = "pin-config" in generated_code
    has_fake_mux_config = "mux-config" in generated_code
    no_hallucination = not has_fake_pin_config and not has_fake_mux_config
    details.append(
        CheckDetail(
            check_name="no_fake_pinctrl_properties",
            passed=no_hallucination,
            expected="No non-existent pin-config or mux-config properties",
            actual="clean" if no_hallucination else f"fake properties: pin-config={has_fake_pin_config}, mux-config={has_fake_mux_config}",
            check_type="hallucination",
        )
    )

    return details
