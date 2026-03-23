"""Static analysis checks for Encrypted MCUboot Image Kconfig fragment."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate encrypted MCUboot Kconfig fragment format and required options."""
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

    # Check 2: CONFIG_BOOT_ENCRYPT_IMAGE=y present
    has_encrypt_image = any("CONFIG_BOOT_ENCRYPT_IMAGE=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="boot_encrypt_image_enabled",
            passed=has_encrypt_image,
            expected="CONFIG_BOOT_ENCRYPT_IMAGE=y",
            actual="present" if has_encrypt_image else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: CONFIG_BOOT_ENCRYPT_RSA=y present
    has_encrypt_rsa = any("CONFIG_BOOT_ENCRYPT_RSA=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="boot_encrypt_rsa_enabled",
            passed=has_encrypt_rsa,
            expected="CONFIG_BOOT_ENCRYPT_RSA=y",
            actual="present" if has_encrypt_rsa else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: CONFIG_BOOT_SIGNATURE_TYPE_RSA=y required by BOOT_ENCRYPT_RSA
    has_sig_rsa = any("CONFIG_BOOT_SIGNATURE_TYPE_RSA=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="boot_signature_type_rsa_enabled",
            passed=has_sig_rsa,
            expected="CONFIG_BOOT_SIGNATURE_TYPE_RSA=y",
            actual="present" if has_sig_rsa else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: CONFIG_BOOT_ENCRYPT_EC256 must NOT appear alongside BOOT_ENCRYPT_RSA
    has_encrypt_ec256 = any("CONFIG_BOOT_ENCRYPT_EC256=y" in line for line in lines)
    no_enc_conflict = not (has_encrypt_rsa and has_encrypt_ec256)
    details.append(
        CheckDetail(
            check_name="no_encryption_type_conflict",
            passed=no_enc_conflict,
            expected="BOOT_ENCRYPT_RSA and BOOT_ENCRYPT_EC256 are mutually exclusive",
            actual="no conflict" if no_enc_conflict else "both BOOT_ENCRYPT_RSA and BOOT_ENCRYPT_EC256 set",
            check_type="constraint",
        )
    )

    # Check 6: Signature type mutual exclusion (RSA and ECDSA_P256 cannot coexist)
    has_sig_ec256 = any("CONFIG_BOOT_SIGNATURE_TYPE_ECDSA_P256=y" in line for line in lines)
    no_sig_conflict = not (has_sig_rsa and has_sig_ec256)
    details.append(
        CheckDetail(
            check_name="no_signature_type_conflict",
            passed=no_sig_conflict,
            expected="BOOT_SIGNATURE_TYPE_RSA and BOOT_SIGNATURE_TYPE_ECDSA_P256 are mutually exclusive",
            actual="no conflict" if no_sig_conflict else "both RSA and ECDSA_P256 signature types set",
            check_type="constraint",
        )
    )

    return details
