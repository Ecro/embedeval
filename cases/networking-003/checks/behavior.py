"""Behavioral checks for TCP client with connection retry."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate TCP retry behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: Retry loop exists (for or while loop with connect inside)
    has_loop = (
        ("for" in generated_code or "while" in generated_code)
        and "zsock_connect" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="retry_loop_present",
            passed=has_loop,
            expected="Loop containing zsock_connect() for retry logic",
            actual="present" if has_loop else "missing — no retry loop",
            check_type="constraint",
        )
    )

    # Check 2: Bounded retry (not infinite) — MAX_RETRIES or numeric bound
    has_bound = (
        "MAX_RETRIES" in generated_code
        or "max_retries" in generated_code
        or "<= 3" in generated_code
        or "< 3" in generated_code
        or "<= MAX" in generated_code
        or "attempt <" in generated_code
        or "retries <" in generated_code
        or "retry <" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="bounded_retry",
            passed=has_bound,
            expected="Retry limited by MAX_RETRIES or numeric bound (not infinite)",
            actual="present" if has_bound else "missing — may be infinite retry",
            check_type="constraint",
        )
    )

    # Check 3: Exponential backoff (delay doubles: *2 or <<1 or 2* pattern)
    has_backoff = (
        "delay *= 2" in generated_code
        or "delay = delay * 2" in generated_code
        or "delay << 1" in generated_code
        or "delay * 2" in generated_code
        or "backoff" in generated_code.lower()
    )
    details.append(
        CheckDetail(
            check_name="exponential_backoff",
            passed=has_backoff,
            expected="Exponential backoff: delay doubles each retry",
            actual="present" if has_backoff else "missing — no exponential growth",
            check_type="constraint",
        )
    )

    # Check 4: k_sleep used for delay (not busy-wait)
    has_sleep = "k_sleep" in generated_code
    details.append(
        CheckDetail(
            check_name="sleep_between_retries",
            passed=has_sleep,
            expected="k_sleep() used for delay between retries",
            actual="present" if has_sleep else "missing — no sleep/delay between retries",
            check_type="exact_match",
        )
    )

    # Check 5: TCP socket type (SOCK_STREAM not SOCK_DGRAM)
    has_stream = "SOCK_STREAM" in generated_code
    has_dgram = "SOCK_DGRAM" in generated_code
    details.append(
        CheckDetail(
            check_name="tcp_socket_type",
            passed=has_stream and not has_dgram,
            expected="SOCK_STREAM for TCP (not SOCK_DGRAM)",
            actual=f"SOCK_STREAM={has_stream}, SOCK_DGRAM={has_dgram}",
            check_type="constraint",
        )
    )

    # Check 6: Connect return value checked
    has_connect_check = "zsock_connect" in generated_code and (
        "== 0" in generated_code or "< 0" in generated_code or "!= 0" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="connect_return_checked",
            passed=has_connect_check,
            expected="zsock_connect() return value checked",
            actual="present" if has_connect_check else "missing — return value ignored",
            check_type="constraint",
        )
    )

    # Check 7: Socket cleanup present (close after all retries fail, or recreate per retry)
    has_close_in_retry = bool(re.search(
        r'(zsock_close|close)\s*\([^)]*\).*zsock_connect',
        generated_code,
        re.DOTALL,
    )) or bool(re.search(
        r'zsock_connect.*?(zsock_close|close)\s*\([^)]*\).*zsock_socket',
        generated_code,
        re.DOTALL,
    ))
    # Also accept: socket closed on final failure (cleanup path)
    has_close_on_fail = bool(re.search(
        r'zsock_close|close\s*\(\s*sock', generated_code
    ))
    details.append(
        CheckDetail(
            check_name="socket_cleanup_on_failure",
            passed=has_close_in_retry or has_close_on_fail,
            expected="Socket closed on failure path (recreate per retry or cleanup after all retries fail)",
            actual="present" if (has_close_in_retry or has_close_on_fail) else "missing — socket leaked on failure",
            check_type="constraint",
        )
    )

    return details
