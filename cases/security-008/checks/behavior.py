"""Behavioral checks for HMAC-SHA256 Message Authentication."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate HMAC-SHA256 behavioral flow properties."""
    details: list[CheckDetail] = []

    # Check 1: init before mac_sign_setup (correct ordering)
    init_pos = generated_code.find("psa_crypto_init")
    setup_pos = generated_code.find("psa_mac_sign_setup")
    init_before_setup = init_pos != -1 and setup_pos != -1 and init_pos < setup_pos
    details.append(
        CheckDetail(
            check_name="init_before_mac_setup",
            passed=init_before_setup,
            expected="psa_crypto_init() before psa_mac_sign_setup()",
            actual="correct order" if init_before_setup else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: setup → update → finish ordering
    update_pos = generated_code.find("psa_mac_update")
    finish_pos = generated_code.find("psa_mac_sign_finish")
    correct_order = (
        setup_pos != -1
        and update_pos != -1
        and finish_pos != -1
        and setup_pos < update_pos < finish_pos
    )
    details.append(
        CheckDetail(
            check_name="mac_setup_update_finish_order",
            passed=correct_order,
            expected="psa_mac_sign_setup → psa_mac_update → psa_mac_sign_finish",
            actual="correct order" if correct_order else "wrong order or missing steps",
            check_type="constraint",
        )
    )

    # Check 3: MAC operation initialized (PSA_MAC_OPERATION_INIT)
    has_op_init = "PSA_MAC_OPERATION_INIT" in generated_code
    details.append(
        CheckDetail(
            check_name="mac_operation_initialized",
            passed=has_op_init,
            expected="psa_mac_operation_t initialized with PSA_MAC_OPERATION_INIT",
            actual="present" if has_op_init else "missing (uninitialized operation risk)",
            check_type="constraint",
        )
    )

    # Check 4: PSA_KEY_TYPE_HMAC used for the key
    has_hmac_key_type = "PSA_KEY_TYPE_HMAC" in generated_code
    details.append(
        CheckDetail(
            check_name="hmac_key_type",
            passed=has_hmac_key_type,
            expected="PSA_KEY_TYPE_HMAC used for HMAC key import",
            actual="present" if has_hmac_key_type else "missing (wrong key type)",
            check_type="constraint",
        )
    )

    # Check 5: Key destroyed after use
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

    # Check 6: Result printed
    has_print = "printk" in generated_code or "printf" in generated_code
    details.append(
        CheckDetail(
            check_name="result_printed",
            passed=has_print,
            expected="MAC result or error printed",
            actual="present" if has_print else "missing",
            check_type="constraint",
        )
    )

    return details
