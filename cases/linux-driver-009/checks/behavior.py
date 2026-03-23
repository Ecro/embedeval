"""Behavioral checks for Linux GPIO consumer driver."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate GPIO consumer driver behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: No legacy gpio_request() — deprecated API
    # (LLM hallucination: using the old integer-based GPIO API)
    has_legacy_request = "gpio_request(" in generated_code
    details.append(
        CheckDetail(
            check_name="no_legacy_gpio_request",
            passed=not has_legacy_request,
            expected="No gpio_request() (deprecated legacy API)",
            actual="clean" if not has_legacy_request else "LEGACY API: gpio_request() found, use devm_gpiod_get()",
            check_type="constraint",
        )
    )

    # Check 2: No legacy gpio_set_value() — deprecated API
    has_legacy_set = "gpio_set_value(" in generated_code
    details.append(
        CheckDetail(
            check_name="no_legacy_gpio_set_value",
            passed=not has_legacy_set,
            expected="No gpio_set_value() (deprecated legacy API)",
            actual="clean" if not has_legacy_set else "LEGACY API: gpio_set_value() found, use gpiod_set_value()",
            check_type="constraint",
        )
    )

    # Check 3: devm_ prefix ensures auto-cleanup (no manual gpio_free needed)
    has_devm = "devm_gpiod_get" in generated_code
    details.append(
        CheckDetail(
            check_name="devm_prefix_for_auto_cleanup",
            passed=has_devm,
            expected="devm_gpiod_get() used (auto-cleanup on driver remove)",
            actual="present" if has_devm else "missing (manual cleanup required without devm_)",
            check_type="constraint",
        )
    )

    # Check 4: Direction set before I/O operations
    # (GPIO must have direction configured before read/write)
    has_direction_before_io = (
        "gpiod_direction_output" in generated_code
        or "gpiod_direction_input" in generated_code
        or "GPIOD_OUT" in generated_code
        or "GPIOD_IN" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="direction_set_before_io",
            passed=has_direction_before_io,
            expected="GPIO direction configured before read/write",
            actual="present" if has_direction_before_io else "missing (direction must be set first)",
            check_type="constraint",
        )
    )

    # Check 5: Error handling for devm_gpiod_get (IS_ERR check)
    has_is_err = "IS_ERR" in generated_code or "PTR_ERR" in generated_code
    details.append(
        CheckDetail(
            check_name="gpiod_get_error_checked",
            passed=has_is_err,
            expected="IS_ERR() check on devm_gpiod_get() return value",
            actual="present" if has_is_err else "missing (NULL/error not checked)",
            check_type="constraint",
        )
    )

    # Check 6: No legacy gpio_free() — should not be needed with devm_
    has_gpio_free = "gpio_free(" in generated_code
    details.append(
        CheckDetail(
            check_name="no_manual_gpio_free",
            passed=not has_gpio_free,
            expected="No manual gpio_free() needed when using devm_gpiod_get()",
            actual="clean" if not has_gpio_free else "unnecessary gpio_free() with devm_ usage",
            check_type="constraint",
        )
    )

    return details
