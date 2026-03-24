"""Behavioral checks for Cryptographically Secure RNG."""

import re

from embedeval.check_utils import (
    extract_error_blocks,
    strip_comments,
)
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate CSPRNG behavioral properties."""
    details: list[CheckDetail] = []

    stripped = strip_comments(generated_code)

    # Check 1: Error path handled - failure message printed
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
    csrand_checked = bool(
        re.search(r"(ret|rc|err|result|status)\s*=\s*sys_csrand_get", generated_code)
        or re.search(r"if\s*\(\s*sys_csrand_get", generated_code)
        or re.search(r"(ret|rc|err|result|status)\s*=\s*psa_generate_random", generated_code)
        or re.search(r"if\s*\(\s*psa_generate_random", generated_code)
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

    # Check 5: No rand()/srand() - use CSPRNG only
    # LLM failure: using C stdlib rand() which is NOT cryptographically secure
    has_rand = bool(re.search(r"\brand\s*\(|\bsrand\s*\(", stripped))
    details.append(
        CheckDetail(
            check_name="no_insecure_rand",
            passed=not has_rand,
            expected="No rand()/srand() - use sys_csrand_get() or psa_generate_random()",
            actual="clean" if not has_rand else "rand()/srand() found - NOT cryptographically secure",
            check_type="constraint",
        )
    )

    # Check 6: Error path returns early (does not proceed with uninitialized buffer)
    # LLM failure: calling RNG, ignoring failure, then treating zeroed buffer as random
    # Note: sys_csrand_get returns int (negative on error), so extract_error_blocks
    # matches the if (ret < 0) pattern correctly here.
    error_blocks = extract_error_blocks(generated_code)
    error_returns = any("return" in block for block in error_blocks)
    details.append(
        CheckDetail(
            check_name="error_path_returns_early",
            passed=error_returns,
            expected="Error path returns early (does not continue with failed RNG output)",
            actual="present" if error_returns else "missing (may use uninitialized entropy)",
            check_type="constraint",
        )
    )

    # Check 7: No ECB mode (general security: no weak algorithm patterns)
    has_ecb = bool(re.search(r"\bECB\b|\bPSA_ALG_ECB\b", stripped))
    details.append(
        CheckDetail(
            check_name="no_ecb_mode",
            passed=not has_ecb,
            expected="No ECB cipher mode in security code",
            actual="clean" if not has_ecb else "ECB mode found (insecure)",
            check_type="constraint",
        )
    )

    return details
