"""Behavioral checks for Cryptographically Secure RNG."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate CSPRNG behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: Error path handled — failure message printed
    has_fail_print = (
        "FAILED" in generated_code
        or "failed" in generated_code
        or "error" in generated_code.lower()
    )
    details.append(
        CheckDetail(
            check_name="error_path_handled",
            passed=has_fail_print,
            expected="Failure case handled with error message",
            actual="present" if has_fail_print else "missing (no error path)",
            check_type="constraint",
        )
    )

    # Check 2: Success path prints result
    has_ok_print = (
        "RNG OK" in generated_code
        or "OK" in generated_code
        or ("printk" in generated_code and "%02x" in generated_code)
        or ("printf" in generated_code and "%02x" in generated_code)
    )
    details.append(
        CheckDetail(
            check_name="success_result_printed",
            passed=has_ok_print,
            expected="Random bytes or success message printed on success",
            actual="present" if has_ok_print else "missing",
            check_type="constraint",
        )
    )

    # Check 3: Return value from RNG used in condition (not silently discarded)
    import re
    # Check that csrand_get result is stored or directly checked
    csrand_checked = bool(
        re.search(r'(ret|rc|err|result|status)\s*=\s*sys_csrand_get', generated_code)
        or re.search(r'if\s*\(\s*sys_csrand_get', generated_code)
        or re.search(r'(ret|rc|err|result|status)\s*=\s*psa_generate_random', generated_code)
        or re.search(r'if\s*\(\s*psa_generate_random', generated_code)
    )
    details.append(
        CheckDetail(
            check_name="rng_return_value_used",
            passed=csrand_checked,
            expected="RNG return value captured and checked (not discarded)",
            actual="return value checked" if csrand_checked else "return value may be discarded",
            check_type="constraint",
        )
    )

    # Check 4: Buffer declared with sufficient size
    buf_pattern = re.search(
        r"uint8_t\s+\w+\s*\[\s*(\w+)\s*\]", generated_code
    )
    buf_ok = False
    buf_size = "unknown"
    if buf_pattern:
        buf_size = buf_pattern.group(1)
        if buf_size.isdigit():
            buf_ok = int(buf_size) >= 32
        else:
            # Named constant — resolve from #define
            define_match = re.search(
                rf"#define\s+{re.escape(buf_size)}\s+(\d+)",
                generated_code,
            )
            if define_match:
                buf_ok = int(define_match.group(1)) >= 32
                buf_size = f"{buf_size}={define_match.group(1)}"
            else:
                buf_ok = True  # Named constant, assume valid
    details.append(
        CheckDetail(
            check_name="buffer_32_bytes_min",
            passed=buf_ok,
            expected="uint8_t buffer of at least 32 bytes declared",
            actual=f"buffer size: {buf_size}",
            check_type="constraint",
        )
    )

    return details
