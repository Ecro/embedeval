"""Behavioral checks for DNS resolution with timeout."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate DNS behavioral properties — timeout, error paths, no infinite waits."""
    details: list[CheckDetail] = []

    # Check 1: Timeout is not infinite (K_FOREVER or 0 means no timeout)
    has_k_forever = "K_FOREVER" in generated_code
    has_zero_timeout = "K_MSEC(0)" in generated_code or "K_SECONDS(0)" in generated_code
    timeout_is_finite = not has_k_forever and not has_zero_timeout
    details.append(
        CheckDetail(
            check_name="timeout_not_infinite",
            passed=timeout_is_finite,
            expected="DNS timeout is a finite value (not K_FOREVER or 0)",
            actual="finite" if timeout_is_finite else "infinite — DNS query may block forever",
            check_type="constraint",
        )
    )

    # Check 2: NXDOMAIN error handled
    has_nxdomain = "DNS_EAI_NONAME" in generated_code or "NXDOMAIN" in generated_code.upper()
    details.append(
        CheckDetail(
            check_name="nxdomain_handled",
            passed=has_nxdomain,
            expected="DNS_EAI_NONAME (NXDOMAIN) handled in callback",
            actual="present" if has_nxdomain else "missing — host-not-found not handled",
            check_type="constraint",
        )
    )

    # Check 3: DNS_EAI_ALLDONE handled (signals query complete)
    has_alldone = "DNS_EAI_ALLDONE" in generated_code
    details.append(
        CheckDetail(
            check_name="alldone_handled",
            passed=has_alldone,
            expected="DNS_EAI_ALLDONE handled — marks end of results",
            actual="present" if has_alldone else "missing — query completion not detected",
            check_type="constraint",
        )
    )

    # Check 4: Error check on dns_resolve_name return value
    has_err_check = "< 0" in generated_code
    details.append(
        CheckDetail(
            check_name="resolve_error_checked",
            passed=has_err_check,
            expected="dns_resolve_name() return value checked for error",
            actual="present" if has_err_check else "missing — DNS call errors silently ignored",
            check_type="constraint",
        )
    )

    # Check 5: DNS_QUERY_TYPE_A used (correct query type for IPv4)
    has_query_type_a = "DNS_QUERY_TYPE_A" in generated_code
    details.append(
        CheckDetail(
            check_name="query_type_a_used",
            passed=has_query_type_a,
            expected="DNS_QUERY_TYPE_A specified for A record lookup",
            actual="present" if has_query_type_a else "missing — query type not set",
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
