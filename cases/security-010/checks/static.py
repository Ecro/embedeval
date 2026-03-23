"""Static analysis checks for PSA ECDSA P-256 Key Pair Generation."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate ECDSA P-256 key generation code structure."""
    details: list[CheckDetail] = []

    # Check 1: psa/crypto.h included
    has_psa_h = "psa/crypto.h" in generated_code
    details.append(
        CheckDetail(
            check_name="psa_crypto_header",
            passed=has_psa_h,
            expected="psa/crypto.h included",
            actual="present" if has_psa_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: PSA_KEY_TYPE_ECC_KEY_PAIR used
    has_ecc_key_pair = "PSA_KEY_TYPE_ECC_KEY_PAIR" in generated_code
    details.append(
        CheckDetail(
            check_name="ecc_key_pair_type",
            passed=has_ecc_key_pair,
            expected="PSA_KEY_TYPE_ECC_KEY_PAIR set for key type",
            actual="present" if has_ecc_key_pair else "missing (wrong key type)",
            check_type="exact_match",
        )
    )

    # Check 3: PSA_ECC_FAMILY_SECP_R1 used (P-256 curve family)
    has_secp_r1 = "PSA_ECC_FAMILY_SECP_R1" in generated_code
    details.append(
        CheckDetail(
            check_name="secp_r1_curve_family",
            passed=has_secp_r1,
            expected="PSA_ECC_FAMILY_SECP_R1 used (P-256 curve)",
            actual="present" if has_secp_r1 else "missing (wrong curve)",
            check_type="exact_match",
        )
    )

    # Check 4: Key bits set to 256
    import re
    bits_256 = bool(re.search(r'psa_set_key_bits\s*\([^,]+,\s*256\s*\)', generated_code))
    details.append(
        CheckDetail(
            check_name="key_bits_256",
            passed=bits_256,
            expected="psa_set_key_bits set to 256 for P-256",
            actual="256 bits set" if bits_256 else "wrong bit size or missing",
            check_type="constraint",
        )
    )

    # Check 5: psa_export_public_key called (not psa_export_key for private key)
    has_export_public = "psa_export_public_key" in generated_code
    details.append(
        CheckDetail(
            check_name="public_key_exported",
            passed=has_export_public,
            expected="psa_export_public_key() called (exports only public key)",
            actual="present" if has_export_public else "missing (may be exporting private key!)",
            check_type="exact_match",
        )
    )

    # Check 6: PSA_KEY_USAGE_EXPORT not set as sole usage (private key protected)
    # Strip comments to avoid matching mentions in comment text
    import re
    code_no_comments = re.sub(r'/\*.*?\*/', '', generated_code, flags=re.DOTALL)
    code_no_comments = re.sub(r'//[^\n]*', '', code_no_comments)
    has_export_usage = "PSA_KEY_USAGE_EXPORT" in code_no_comments
    details.append(
        CheckDetail(
            check_name="no_private_export_usage",
            passed=not has_export_usage,
            expected="PSA_KEY_USAGE_EXPORT not set (private key non-extractable)",
            actual="EXPORT usage flag set (private key extractable!)" if has_export_usage else "correct (no EXPORT flag)",
            check_type="constraint",
        )
    )

    # Check 7: psa_generate_key called (not psa_import_key for generated keys)
    has_generate = "psa_generate_key" in generated_code
    details.append(
        CheckDetail(
            check_name="psa_generate_key_called",
            passed=has_generate,
            expected="psa_generate_key() called to generate key pair",
            actual="present" if has_generate else "missing",
            check_type="exact_match",
        )
    )

    return details
