"""Static analysis checks for Zephyr Shell with Logging Backend Kconfig fragment."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate shell+logging Kconfig fragment format and required options."""
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

    # Check 2: CONFIG_SHELL=y present
    has_shell = any("CONFIG_SHELL=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="shell_enabled",
            passed=has_shell,
            expected="CONFIG_SHELL=y",
            actual="present" if has_shell else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: CONFIG_SHELL_LOG_BACKEND=y present
    has_shell_log = any("CONFIG_SHELL_LOG_BACKEND=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="shell_log_backend_enabled",
            passed=has_shell_log,
            expected="CONFIG_SHELL_LOG_BACKEND=y",
            actual="present" if has_shell_log else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: CONFIG_LOG=y present (dependency for SHELL_LOG_BACKEND)
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

    # Check 5: CONFIG_LOG_MINIMAL=y must NOT be present (mutual exclusion with SHELL_LOG_BACKEND)
    no_log_minimal = not any("CONFIG_LOG_MINIMAL=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="log_minimal_absent",
            passed=no_log_minimal,
            expected="CONFIG_LOG_MINIMAL=y absent (incompatible with SHELL_LOG_BACKEND)",
            actual="not present" if no_log_minimal else "CONFIG_LOG_MINIMAL=y found (conflicts with SHELL_LOG_BACKEND)",
            check_type="constraint",
        )
    )

    return details
