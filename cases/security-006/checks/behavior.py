"""Behavioral checks for Secure Key Storage with Anti-Tamper."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate non-extractable key behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: psa_crypto_init before psa_import_key (correct ordering)
    init_pos = generated_code.find("psa_crypto_init")
    import_pos = generated_code.find("psa_import_key")
    init_before_import = init_pos != -1 and import_pos != -1 and init_pos < import_pos
    details.append(
        CheckDetail(
            check_name="init_before_import",
            passed=init_before_import,
            expected="psa_crypto_init() before psa_import_key()",
            actual="correct order" if init_before_import else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: psa_export_key called to verify denial (anti-tamper verification)
    has_export_call = "psa_export_key" in generated_code
    details.append(
        CheckDetail(
            check_name="export_denial_verified",
            passed=has_export_call,
            expected="psa_export_key() called to verify export is denied",
            actual="present" if has_export_call else "missing (no verification of non-extractability)",
            check_type="constraint",
        )
    )

    # Check 3: PSA_ERROR_NOT_PERMITTED checked (correct denial status)
    has_not_permitted = "PSA_ERROR_NOT_PERMITTED" in generated_code
    details.append(
        CheckDetail(
            check_name="not_permitted_checked",
            passed=has_not_permitted,
            expected="PSA_ERROR_NOT_PERMITTED checked after psa_export_key()",
            actual="present" if has_not_permitted else "missing (export denial not detected)",
            check_type="constraint",
        )
    )

    # Check 4: psa_destroy_key called (no key leak)
    has_destroy = "psa_destroy_key" in generated_code
    details.append(
        CheckDetail(
            check_name="key_destroyed",
            passed=has_destroy,
            expected="psa_destroy_key() called to clean up key slot",
            actual="present" if has_destroy else "missing (key slot leak)",
            check_type="constraint",
        )
    )

    # Check 5: Key attributes initialized (PSA_KEY_ATTRIBUTES_INIT)
    has_attrs_init = "PSA_KEY_ATTRIBUTES_INIT" in generated_code
    details.append(
        CheckDetail(
            check_name="attributes_initialized",
            passed=has_attrs_init,
            expected="PSA_KEY_ATTRIBUTES_INIT used to zero-initialize key attributes",
            actual="present" if has_attrs_init else "missing (uninitialized attributes risk)",
            check_type="constraint",
        )
    )

    # Check 6: Result printed (KEY SECURE or equivalent)
    has_print = "printk" in generated_code or "printf" in generated_code
    details.append(
        CheckDetail(
            check_name="result_printed",
            passed=has_print,
            expected="Result printed (KEY SECURE / KEY EXPOSED)",
            actual="present" if has_print else "missing",
            check_type="constraint",
        )
    )

    return details
