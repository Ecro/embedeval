"""Behavioral checks for Device Tree pinctrl UART overlay."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Device Tree pinctrl behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: pinctrl-names = "default" (correct state name)
    has_default_name = 'pinctrl-names = "default"' in generated_code
    details.append(
        CheckDetail(
            check_name="pinctrl_names_default",
            passed=has_default_name,
            expected='pinctrl-names = "default"',
            actual="present" if has_default_name else "missing or wrong state name",
            check_type="exact_match",
        )
    )

    # Check 2: pinctrl-0 references a pinctrl phandle (contains &)
    has_phandle_ref = "pinctrl-0 = <&" in generated_code
    details.append(
        CheckDetail(
            check_name="pinctrl_0_references_phandle",
            passed=has_phandle_ref,
            expected="pinctrl-0 references a phandle (e.g. <&uart0_default>)",
            actual="present" if has_phandle_ref else "missing phandle reference",
            check_type="constraint",
        )
    )

    # Check 3: pinctrl node or state definition present
    has_pinctrl_node = "&pinctrl" in generated_code or "pinctrl {" in generated_code or "_default" in generated_code
    details.append(
        CheckDetail(
            check_name="pinctrl_state_defined",
            passed=has_pinctrl_node,
            expected="pinctrl state node defined (e.g. uart0_default)",
            actual="present" if has_pinctrl_node else "missing pinctrl state definition",
            check_type="constraint",
        )
    )

    # Check 4: status = "okay" on uart0
    has_status_okay = 'status = "okay"' in generated_code
    details.append(
        CheckDetail(
            check_name="uart0_status_okay",
            passed=has_status_okay,
            expected='status = "okay" on uart0',
            actual="present" if has_status_okay else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: No Linux kernel-style pin-config usage (cross-platform confusion)
    has_linux_pinctrl = "PIN_MAP" in generated_code or "PINCTRL_PIN(" in generated_code
    no_linux_style = not has_linux_pinctrl
    details.append(
        CheckDetail(
            check_name="no_linux_pinctrl_style",
            passed=no_linux_style,
            expected="Zephyr DT pinctrl syntax, not Linux kernel PIN_MAP style",
            actual="clean" if no_linux_style else "Linux kernel pinctrl API used (wrong context)",
            check_type="hallucination",
        )
    )

    return details
