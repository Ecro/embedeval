"""Behavioral checks for PSA Protected Storage."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate PSA Protected Storage behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: init before ps_set (correct ordering)
    init_pos = generated_code.find("psa_crypto_init")
    set_pos = generated_code.find("psa_ps_set")
    details.append(
        CheckDetail(
            check_name="init_before_ps_set",
            passed=init_pos != -1 and set_pos != -1 and init_pos < set_pos,
            expected="psa_crypto_init() before psa_ps_set()",
            actual="correct order" if (init_pos != -1 and set_pos != -1 and init_pos < set_pos) else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: ps_set before ps_get (must store before retrieve)
    get_pos = generated_code.find("psa_ps_get")
    details.append(
        CheckDetail(
            check_name="ps_set_before_ps_get",
            passed=set_pos != -1 and get_pos != -1 and set_pos < get_pos,
            expected="psa_ps_set() before psa_ps_get()",
            actual="correct order" if (set_pos != -1 and get_pos != -1 and set_pos < get_pos) else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 3: actual_length variable captured from psa_ps_get
    # LLM failure: no size output variable, can't detect truncation
    import re
    has_actual_len = bool(
        re.search(r'\b\w*(actual|out|result)\w*_len\w*\b|\bactual_length\b|\bout_len\b', generated_code)
        or re.search(r'psa_ps_get\s*\([^)]*&', generated_code)
    )
    details.append(
        CheckDetail(
            check_name="actual_length_captured",
            passed=has_actual_len,
            expected="actual_length output parameter captured from psa_ps_get",
            actual="present" if has_actual_len else "missing (buffer overrun risk)",
            check_type="constraint",
        )
    )

    # Check 4: Retrieved data verified against original (memcmp)
    has_memcmp = "memcmp" in generated_code
    details.append(
        CheckDetail(
            check_name="data_verified_after_get",
            passed=has_memcmp,
            expected="memcmp() verifies retrieved data matches stored data",
            actual="present" if has_memcmp else "missing (no data integrity check)",
            check_type="constraint",
        )
    )

    # Check 5: Result printed
    has_print = "printk" in generated_code or "printf" in generated_code
    details.append(
        CheckDetail(
            check_name="result_printed",
            passed=has_print,
            expected="Result printed (PS OK / PS FAILED)",
            actual="present" if has_print else "missing",
            check_type="constraint",
        )
    )

    # Check 6: PSA_STORAGE_FLAG_NONE used (or a valid flag constant)
    has_storage_flag = (
        "PSA_STORAGE_FLAG_NONE" in generated_code
        or "PSA_STORAGE_FLAG_" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="storage_flag_specified",
            passed=has_storage_flag,
            expected="PSA_STORAGE_FLAG_NONE or valid flag in psa_ps_set",
            actual="present" if has_storage_flag else "missing (0 used as flag?)",
            check_type="constraint",
        )
    )

    return details
