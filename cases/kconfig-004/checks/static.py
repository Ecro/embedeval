"""Static analysis checks for Zephyr logging Kconfig fragment."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate logging Kconfig fragment format and required options."""
    details: list[CheckDetail] = []
    lines = [
        line.strip()
        for line in generated_code.strip().splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    # Check 1: All lines use CONFIG_ prefix and contain =
    valid_format = all(
        line.startswith("CONFIG_") and "=" in line for line in lines
    )
    details.append(
        CheckDetail(
            check_name="kconfig_format",
            passed=valid_format,
            expected="All lines start with CONFIG_ and contain =",
            actual=f"{len(lines)} lines, format valid: {valid_format}",
            check_type="exact_match",
        )
    )

    # Check 2: CONFIG_LOG=y present
    has_log = any("CONFIG_LOG=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="log_enabled",
            passed=has_log,
            expected="CONFIG_LOG=y",
            actual="present" if has_log else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: CONFIG_LOG_BACKEND_UART=y present
    has_uart_backend = any("CONFIG_LOG_BACKEND_UART=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="log_backend_uart_enabled",
            passed=has_uart_backend,
            expected="CONFIG_LOG_BACKEND_UART=y",
            actual="present" if has_uart_backend else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: CONFIG_LOG_MODE_DEFERRED=y present
    has_deferred = any("CONFIG_LOG_MODE_DEFERRED=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="log_mode_deferred_enabled",
            passed=has_deferred,
            expected="CONFIG_LOG_MODE_DEFERRED=y",
            actual="present" if has_deferred else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: CONFIG_LOG_BUFFER_SIZE is set
    has_buffer_size = any("CONFIG_LOG_BUFFER_SIZE=" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="log_buffer_size_set",
            passed=has_buffer_size,
            expected="CONFIG_LOG_BUFFER_SIZE=<value>",
            actual="present" if has_buffer_size else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: LOG_MODE_IMMEDIATE not enabled (conflicts with DEFERRED)
    no_immediate = not any("CONFIG_LOG_MODE_IMMEDIATE=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="no_log_mode_immediate_conflict",
            passed=no_immediate,
            expected="CONFIG_LOG_MODE_IMMEDIATE not enabled",
            actual="not present" if no_immediate else "CONFIG_LOG_MODE_IMMEDIATE=y found",
            check_type="constraint",
        )
    )

    return details
