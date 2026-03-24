"""Behavioral checks for Device Tree pinctrl UART overlay."""

from embedeval.models import CheckDetail

_FAKE_DT_PROPERTIES = [
    "pin-config",      # LLM commonly hallucinates this; correct is pinctrl-0
    "mux-config",
    "clock-speed",
]


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Device Tree pinctrl behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: No fake DT properties — especially pin-config (should be pinctrl-0)
    found_fake = [prop for prop in _FAKE_DT_PROPERTIES if prop in generated_code]
    details.append(
        CheckDetail(
            check_name="no_fake_dt_properties",
            passed=not found_fake,
            expected="No hallucinated DT properties; pin-config does not exist (use pinctrl-0)",
            actual="clean" if not found_fake else f"fake properties found: {found_fake}",
            check_type="hallucination",
        )
    )

    # Check 2: pinctrl-names = "default" (correct state name)
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

    # Check 3: pinctrl-0 references a pinctrl phandle (contains &)
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

    # Check 4: pinctrl state definition present
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

    # Check 5: status = "okay" on uart0
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

    # Check 6: No Linux kernel-style pin-config usage (cross-platform confusion)
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

    # Check 7: uart0 or uart node referenced (not a made-up node)
    has_uart0 = "&uart0" in generated_code
    details.append(
        CheckDetail(
            check_name="uart0_node_referenced",
            passed=has_uart0,
            expected="&uart0 node referenced in overlay",
            actual="present" if has_uart0 else "missing — uart0 not referenced",
            check_type="constraint",
        )
    )

    # Check 8: pinctrl-0 and pinctrl-names appear together (both required)
    has_pinctrl_pair = (
        "pinctrl-0" in generated_code
        and "pinctrl-names" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="pinctrl_pair_present",
            passed=has_pinctrl_pair,
            expected="Both pinctrl-0 and pinctrl-names must be specified together",
            actual="present" if has_pinctrl_pair else "one or both of pinctrl-0/pinctrl-names missing",
            check_type="constraint",
        )
    )

    return details
