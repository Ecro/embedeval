"""Static analysis checks for Basic MCUboot Logging Kconfig fragment."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate basic MCUboot logging Kconfig fragment format and required options."""
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
            expected="All lines: CONFIG_*=value",
            actual=f"{len(lines)} lines, valid={valid_format}",
            check_type="exact_match",
        )
    )

    # Check 2: CONFIG_BOOTLOADER_MCUBOOT=y present
    has_mcuboot = any("CONFIG_BOOTLOADER_MCUBOOT=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="mcuboot_enabled",
            passed=has_mcuboot,
            expected="CONFIG_BOOTLOADER_MCUBOOT=y",
            actual="present" if has_mcuboot else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: CONFIG_MCUBOOT_LOG_LEVEL_DBG=y present
    has_log_dbg = any("CONFIG_MCUBOOT_LOG_LEVEL_DBG=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="mcuboot_log_level_dbg_enabled",
            passed=has_log_dbg,
            expected="CONFIG_MCUBOOT_LOG_LEVEL_DBG=y",
            actual="present" if has_log_dbg else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: CONFIG_LOG=y present (required for MCUBOOT_LOG_LEVEL_DBG)
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

    # Check 5: CONFIG_BOOT_BANNER=y present
    has_banner = any("CONFIG_BOOT_BANNER=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="boot_banner_enabled",
            passed=has_banner,
            expected="CONFIG_BOOT_BANNER=y",
            actual="present" if has_banner else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: CONFIG_LOG_MINIMAL must NOT be present (disables debug level)
    no_log_minimal = not any("CONFIG_LOG_MINIMAL=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="log_minimal_absent",
            passed=no_log_minimal,
            expected="CONFIG_LOG_MINIMAL=y absent (would suppress debug log output)",
            actual="not present" if no_log_minimal else "CONFIG_LOG_MINIMAL=y found (conflicts with DBG level)",
            check_type="constraint",
        )
    )

    return details
