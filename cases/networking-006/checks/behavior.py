"""Behavioral checks for TCP server with buffer overflow protection."""

import re

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate TCP server safety and correctness behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: Null-terminate received data — must be buf[len] = '\0' pattern
    # (not just any occurrence of \0 in the source)
    has_null_term = bool(re.search(
        r'\w+\s*\[\s*\w+\s*\]\s*=\s*[\'\"]\\0[\'\"]', generated_code
    )) or bool(re.search(
        r'\w+\s*\[\s*\w+\s*\]\s*=\s*0\s*;', generated_code
    ))
    details.append(
        CheckDetail(
            check_name="null_terminate_received",
            passed=has_null_term,
            expected="Received buffer null-terminated after recv",
            actual="present" if has_null_term else "missing — string operations on unterminated buffer",
            check_type="constraint",
        )
    )

    # Check 2: Error check on recv return (< 0 or <= 0)
    has_recv_err = "< 0" in generated_code or "<= 0" in generated_code
    details.append(
        CheckDetail(
            check_name="recv_error_check",
            passed=has_recv_err,
            expected="zsock_recv return value checked for error (< 0)",
            actual="present" if has_recv_err else "missing — recv errors ignored",
            check_type="constraint",
        )
    )

    # Check 3: Connection-closed check (ret == 0) — scoped to recv context
    has_closed_check = bool(re.search(
        r'(?:ret|len|n|bytes)\s*==\s*0', generated_code
    )) and ("recv" in generated_code)
    details.append(
        CheckDetail(
            check_name="connection_closed_check",
            passed=has_closed_check,
            expected="recv return value == 0 handled (connection closed)",
            actual="present" if has_closed_check else "missing — closed connection not detected",
            check_type="constraint",
        )
    )

    # Check 4: recv size is strictly less than buffer (sizeof - 1 pattern)
    # Catches the CWE-120 pattern where recv fills entire buffer with no room for '\0'
    has_minus_one = "sizeof(recv_buf) - 1" in generated_code or "RECV_BUF_SIZE - 1" in generated_code
    details.append(
        CheckDetail(
            check_name="recv_minus_one_for_null",
            passed=has_minus_one,
            expected="recv size is sizeof(buf) - 1 to leave room for null terminator",
            actual="present" if has_minus_one else "missing — may overwrite null byte position",
            check_type="constraint",
        )
    )

    # Check 5: Both sockets closed (resource cleanup)
    close_count = generated_code.count("zsock_close(")
    details.append(
        CheckDetail(
            check_name="both_sockets_closed",
            passed=close_count >= 2,
            expected="Both server and client sockets closed",
            actual=f"{close_count} zsock_close() calls found",
            check_type="constraint",
        )
    )

    # Check 6: No POSIX recv() — should use zsock_recv
    uses_posix_recv = " recv(" in generated_code and "zsock_recv" not in generated_code
    details.append(
        CheckDetail(
            check_name="uses_zsock_recv",
            passed=not uses_posix_recv,
            expected="zsock_recv() used (Zephyr API)",
            actual="correct" if not uses_posix_recv else "POSIX recv() used — not portable in Zephyr",
            check_type="exact_match",
        )
    )

    # Check: No cross-platform API contamination
    cross_plat = check_no_cross_platform_apis(generated_code, skip_platforms=["Linux_Userspace"])
    details.append(CheckDetail(
        check_name="no_cross_platform_apis",
        passed=len(cross_plat) == 0,
        expected="No FreeRTOS/Arduino/STM32_HAL/POSIX APIs",
        actual="clean" if not cross_plat else f"found: {[a for a, _ in cross_plat]}",
        check_type="constraint",
    ))

    return details
