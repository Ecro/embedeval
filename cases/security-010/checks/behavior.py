"""Behavioral checks for PSA ECDSA P-256 Key Pair Generation."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate ECDSA P-256 key generation behavioral flow."""
    details: list[CheckDetail] = []

    # Check 1: init before generate
    init_pos = generated_code.find("psa_crypto_init")
    generate_pos = generated_code.find("psa_generate_key")
    init_before_gen = init_pos != -1 and generate_pos != -1 and init_pos < generate_pos
    details.append(
        CheckDetail(
            check_name="init_before_generate",
            passed=init_before_gen,
            expected="psa_crypto_init() before psa_generate_key()",
            actual="correct order" if init_before_gen else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: generate before export_public_key
    export_pub_pos = generated_code.find("psa_export_public_key")
    gen_before_export = (
        generate_pos != -1
        and export_pub_pos != -1
        and generate_pos < export_pub_pos
    )
    details.append(
        CheckDetail(
            check_name="generate_before_export_public",
            passed=gen_before_export,
            expected="psa_generate_key() before psa_export_public_key()",
            actual="correct order" if gen_before_export else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 3: Key attributes initialized
    has_attrs_init = "PSA_KEY_ATTRIBUTES_INIT" in generated_code
    details.append(
        CheckDetail(
            check_name="attributes_initialized",
            passed=has_attrs_init,
            expected="PSA_KEY_ATTRIBUTES_INIT used",
            actual="present" if has_attrs_init else "missing",
            check_type="constraint",
        )
    )

    # Check 4: Key destroyed after use
    has_destroy = "psa_destroy_key" in generated_code
    details.append(
        CheckDetail(
            check_name="key_destroyed",
            passed=has_destroy,
            expected="psa_destroy_key() called to release key slot",
            actual="present" if has_destroy else "missing (key slot leak)",
            check_type="constraint",
        )
    )

    # Check 5: PSA_SUCCESS used for return value checks
    has_psa_success = "PSA_SUCCESS" in generated_code
    details.append(
        CheckDetail(
            check_name="psa_success_checked",
            passed=has_psa_success,
            expected="PSA_SUCCESS used for return value checks",
            actual="present" if has_psa_success else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: Result printed
    has_print = "printk" in generated_code or "printf" in generated_code
    details.append(
        CheckDetail(
            check_name="result_printed",
            passed=has_print,
            expected="Result or key info printed",
            actual="present" if has_print else "missing",
            check_type="constraint",
        )
    )

    return details
