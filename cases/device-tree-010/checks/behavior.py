"""Behavioral checks for Device Tree chosen node and aliases."""

from embedeval.models import CheckDetail

_FAKE_DT_PROPERTIES = [
    "pin-config",
    "mux-config",
    "clock-speed",
]


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Device Tree chosen/aliases behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: No fake DT properties
    found_fake = [prop for prop in _FAKE_DT_PROPERTIES if prop in generated_code]
    details.append(
        CheckDetail(
            check_name="no_fake_dt_properties",
            passed=not found_fake,
            expected="No hallucinated DT properties (pin-config, mux-config, clock-speed)",
            actual="clean" if not found_fake else f"fake properties found: {found_fake}",
            check_type="hallucination",
        )
    )

    # Check 2: zephyr,console = &uart0 (references real node)
    has_console_uart0 = "zephyr,console = &uart0" in generated_code
    details.append(
        CheckDetail(
            check_name="console_references_uart0",
            passed=has_console_uart0,
            expected="zephyr,console = &uart0",
            actual="present" if has_console_uart0 else "missing or wrong node reference",
            check_type="exact_match",
        )
    )

    # Check 3: zephyr,shell-uart property present
    has_shell_uart = "zephyr,shell-uart" in generated_code
    details.append(
        CheckDetail(
            check_name="shell_uart_present",
            passed=has_shell_uart,
            expected="zephyr,shell-uart property in chosen",
            actual="present" if has_shell_uart else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Aliases use &label references (phandle syntax)
    has_alias_phandle = (
        "led0 = &" in generated_code or "led0 = &" in generated_code.replace(" ", "")
    )
    details.append(
        CheckDetail(
            check_name="alias_uses_phandle_reference",
            passed=has_alias_phandle,
            expected="Aliases use &label phandle references (e.g. led0 = &led_0)",
            actual="present" if has_alias_phandle else "missing or using string path instead of phandle",
            check_type="constraint",
        )
    )

    # Check 5: sw0 alias present
    has_sw0 = "sw0" in generated_code
    details.append(
        CheckDetail(
            check_name="sw0_alias_present",
            passed=has_sw0,
            expected="sw0 alias defined in aliases",
            actual="present" if has_sw0 else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: No string path aliases (hallucination: led0 = "/leds/led_0"; is wrong)
    has_string_path_alias = (
        'led0 = "/' in generated_code
        or 'sw0 = "/' in generated_code
    )
    no_string_path = not has_string_path_alias
    details.append(
        CheckDetail(
            check_name="no_string_path_aliases",
            passed=no_string_path,
            expected="Aliases use &label references, not string paths",
            actual="clean" if no_string_path else "string path used in alias (wrong format - use &label)",
            check_type="hallucination",
        )
    )

    # Check 7: chosen properties reference uart0 (not a made-up node)
    chosen_refs_real_node = "&uart0" in generated_code
    details.append(
        CheckDetail(
            check_name="chosen_references_real_uart_node",
            passed=chosen_refs_real_node,
            expected="chosen references &uart0 (real Zephyr node label)",
            actual="present" if chosen_refs_real_node else "uart0 not referenced - may use non-existent node",
            check_type="constraint",
        )
    )

    # Check 8: gpio-leds compatible for LED nodes (LLM failure: uses wrong compatible)
    # If the DT defines LED nodes, they should use gpio-leds compatible
    if "led" in generated_code.lower() and "gpios" in generated_code:
        has_gpio_leds = 'compatible = "gpio-leds"' in generated_code
    else:
        has_gpio_leds = True  # No LED gpios present, pass
    details.append(
        CheckDetail(
            check_name="gpio_leds_compatible",
            passed=has_gpio_leds,
            expected='LED nodes with gpios property use compatible = "gpio-leds"',
            actual="present" if has_gpio_leds else "missing — gpio-leds compatible required for LED nodes",
            check_type="constraint",
        )
    )

    # Check 9: gpio-keys compatible for button nodes
    if "button" in generated_code.lower() and "gpios" in generated_code:
        has_gpio_keys = 'compatible = "gpio-keys"' in generated_code
    else:
        has_gpio_keys = True
    details.append(
        CheckDetail(
            check_name="gpio_keys_compatible",
            passed=has_gpio_keys,
            expected='Button nodes with gpios property use compatible = "gpio-keys"',
            actual="present" if has_gpio_keys else "missing — gpio-keys compatible required for button nodes",
            check_type="constraint",
        )
    )

    return details
