"""Static analysis checks for U-Boot Environment Kconfig."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate U-Boot Kconfig structure."""
    details: list[CheckDetail] = []
    lines = [
        line.strip()
        for line in generated_code.strip().splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    # Check 1: valid Kconfig format
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

    # Check 2: MCUboot NOT enabled (U-Boot path)
    no_mcuboot = not any("CONFIG_BOOTLOADER_MCUBOOT=y" in l for l in lines)
    details.append(
        CheckDetail(
            check_name="mcuboot_not_enabled",
            passed=no_mcuboot,
            expected="CONFIG_BOOTLOADER_MCUBOOT not enabled (U-Boot path)",
            actual="not present" if no_mcuboot else "present (conflicts with U-Boot)",
            check_type="constraint",
        )
    )

    # Check 3: BOOT_DELAY set
    has_boot_delay = any("CONFIG_BOOT_DELAY=" in l for l in lines)
    details.append(
        CheckDetail(
            check_name="boot_delay_set",
            passed=has_boot_delay,
            expected="CONFIG_BOOT_DELAY=<value> set",
            actual="present" if has_boot_delay else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: CMD_ENV enabled
    has_cmd_env = any("CONFIG_CMD_ENV=y" in l for l in lines)
    details.append(
        CheckDetail(
            check_name="cmd_env_enabled",
            passed=has_cmd_env,
            expected="CONFIG_CMD_ENV=y",
            actual="present" if has_cmd_env else "missing",
            check_type="exact_match",
        )
    )

    return details
