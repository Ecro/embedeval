"""Static analysis checks for Device Tree chosen node and aliases overlay."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Device Tree chosen/aliases overlay syntax and structure."""
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

    # Check 2: chosen node present
    has_chosen = "chosen" in generated_code and "{" in generated_code
    details.append(
        CheckDetail(
            check_name="chosen_node_present",
            passed=has_chosen,
            expected="chosen node block present",
            actual="present" if has_chosen else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: aliases node present
    has_aliases = "aliases" in generated_code
    details.append(
        CheckDetail(
            check_name="aliases_node_present",
            passed=has_aliases,
            expected="aliases node present",
            actual="present" if has_aliases else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: zephyr,console property
    has_console = "zephyr,console" in generated_code
    details.append(
        CheckDetail(
            check_name="zephyr_console_present",
            passed=has_console,
            expected="zephyr,console property present in chosen",
            actual="present" if has_console else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: led0 alias present
    has_led0 = "led0" in generated_code
    details.append(
        CheckDetail(
            check_name="led0_alias_present",
            passed=has_led0,
            expected="led0 alias defined",
            actual="present" if has_led0 else "missing",
            check_type="exact_match",
        )
    )

    return details
