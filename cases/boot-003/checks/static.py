"""Static analysis checks for Secure Boot with Signing Kconfig."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate secure boot Kconfig structure."""
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

    # Check 2: MCUboot enabled
    has_mcuboot = any("CONFIG_BOOTLOADER_MCUBOOT=y" in l for l in lines)
    details.append(
        CheckDetail(
            check_name="mcuboot_enabled",
            passed=has_mcuboot,
            expected="CONFIG_BOOTLOADER_MCUBOOT=y",
            actual="present" if has_mcuboot else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: RSA signature type set
    has_rsa = any("CONFIG_BOOT_SIGNATURE_TYPE_RSA=y" in l for l in lines)
    details.append(
        CheckDetail(
            check_name="rsa_signature_type",
            passed=has_rsa,
            expected="CONFIG_BOOT_SIGNATURE_TYPE_RSA=y",
            actual="present" if has_rsa else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Key file specified
    has_key_file = any("CONFIG_BOOT_SIGNATURE_KEY_FILE=" in l for l in lines)
    details.append(
        CheckDetail(
            check_name="signature_key_file",
            passed=has_key_file,
            expected="CONFIG_BOOT_SIGNATURE_KEY_FILE=<path>",
            actual="present" if has_key_file else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: FLASH enabled
    has_flash = any("CONFIG_FLASH=y" in l for l in lines)
    details.append(
        CheckDetail(
            check_name="flash_enabled",
            passed=has_flash,
            expected="CONFIG_FLASH=y",
            actual="present" if has_flash else "missing",
            check_type="exact_match",
        )
    )

    return details
