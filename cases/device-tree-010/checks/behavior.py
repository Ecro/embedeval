"""Behavioral checks for Device Tree chosen node and aliases."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Device Tree chosen/aliases behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: zephyr,console = &uart0 (references real node)
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

    # Check 2: zephyr,shell-uart property present
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

    # Check 3: Aliases use &label references (phandle syntax)
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

    # Check 4: sw0 alias present
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

    # Check 5: No string path aliases (hallucination: led0 = "/leds/led_0"; is wrong)
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

    # Check 6: chosen properties reference uart0 (not a made-up node)
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

    return details
