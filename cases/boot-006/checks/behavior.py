"""Behavioral checks for Encrypted MCUboot Image Kconfig fragment."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate encrypted MCUboot Kconfig dependency chains and mutual exclusion invariants."""
    details: list[CheckDetail] = []
    config: dict[str, str] = {}
    for line in generated_code.strip().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            config[key.strip()] = val.strip()

    encrypt_image_enabled = config.get("CONFIG_BOOT_ENCRYPT_IMAGE") == "y"
    encrypt_rsa_enabled = config.get("CONFIG_BOOT_ENCRYPT_RSA") == "y"
    encrypt_ec256_enabled = config.get("CONFIG_BOOT_ENCRYPT_EC256") == "y"
    sig_rsa_enabled = config.get("CONFIG_BOOT_SIGNATURE_TYPE_RSA") == "y"
    sig_ec256_enabled = config.get("CONFIG_BOOT_SIGNATURE_TYPE_ECDSA_P256") == "y"

    # Metamorphic: BOOT_ENCRYPT_RSA requires BOOT_ENCRYPT_IMAGE=y
    encrypt_rsa_needs_base = not (encrypt_rsa_enabled and not encrypt_image_enabled)
    details.append(
        CheckDetail(
            check_name="boot_encrypt_rsa_requires_encrypt_image",
            passed=encrypt_rsa_needs_base,
            expected="BOOT_ENCRYPT_RSA requires BOOT_ENCRYPT_IMAGE=y",
            actual=(
                f"BOOT_ENCRYPT_IMAGE={config.get('CONFIG_BOOT_ENCRYPT_IMAGE', 'n')}, "
                f"BOOT_ENCRYPT_RSA={config.get('CONFIG_BOOT_ENCRYPT_RSA', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Metamorphic: BOOT_ENCRYPT_RSA requires BOOT_SIGNATURE_TYPE_RSA=y
    encrypt_rsa_needs_sig = not (encrypt_rsa_enabled and not sig_rsa_enabled)
    details.append(
        CheckDetail(
            check_name="boot_encrypt_rsa_requires_signature_rsa",
            passed=encrypt_rsa_needs_sig,
            expected="BOOT_ENCRYPT_RSA requires BOOT_SIGNATURE_TYPE_RSA=y",
            actual=(
                f"BOOT_SIGNATURE_TYPE_RSA={config.get('CONFIG_BOOT_SIGNATURE_TYPE_RSA', 'n')}, "
                f"BOOT_ENCRYPT_RSA={config.get('CONFIG_BOOT_ENCRYPT_RSA', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Mutual exclusion: BOOT_ENCRYPT_RSA and BOOT_ENCRYPT_EC256 cannot coexist
    no_enc_conflict = not (encrypt_rsa_enabled and encrypt_ec256_enabled)
    details.append(
        CheckDetail(
            check_name="encryption_type_mutual_exclusion",
            passed=no_enc_conflict,
            expected="BOOT_ENCRYPT_RSA and BOOT_ENCRYPT_EC256 are mutually exclusive",
            actual=(
                "no conflict"
                if no_enc_conflict
                else "both BOOT_ENCRYPT_RSA and BOOT_ENCRYPT_EC256 set"
            ),
            check_type="constraint",
        )
    )

    # Mutual exclusion: signature types RSA and ECDSA_P256 cannot coexist
    no_sig_conflict = not (sig_rsa_enabled and sig_ec256_enabled)
    details.append(
        CheckDetail(
            check_name="signature_type_mutual_exclusion",
            passed=no_sig_conflict,
            expected="BOOT_SIGNATURE_TYPE_RSA and BOOT_SIGNATURE_TYPE_ECDSA_P256 are mutually exclusive",
            actual=(
                "no conflict"
                if no_sig_conflict
                else "both RSA and ECDSA_P256 signature types set"
            ),
            check_type="constraint",
        )
    )

    # Summary: all required configs present
    required = [
        "CONFIG_BOOT_ENCRYPT_IMAGE",
        "CONFIG_BOOT_ENCRYPT_RSA",
        "CONFIG_BOOT_SIGNATURE_TYPE_RSA",
    ]
    all_present = all(config.get(k) == "y" for k in required)
    details.append(
        CheckDetail(
            check_name="all_required_configs_enabled",
            passed=all_present,
            expected="BOOT_ENCRYPT_IMAGE, BOOT_ENCRYPT_RSA, BOOT_SIGNATURE_TYPE_RSA all =y",
            actual=str({k: config.get(k, "missing") for k in required}),
            check_type="exact_match",
        )
    )

    return details
