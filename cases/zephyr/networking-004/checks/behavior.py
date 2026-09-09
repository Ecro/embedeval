"""Behavioral checks for CoAP client GET request."""

from embedeval.models import CheckDetail
from embedeval.check_utils import function_bodies
from embedeval.check_utils import check_no_cross_platform_apis
from embedeval.check_utils import scoped_contains
from embedeval.check_utils import find_in_code


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate CoAP client behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: CON message type used (reliable delivery), not NON
    has_con = scoped_contains(generated_code, 'COAP_TYPE_CON', scope='code_only')
    has_non = scoped_contains(generated_code, 'COAP_TYPE_NON', scope='code_only')
    details.append(
        CheckDetail(
            check_name="coap_con_message_type",
            passed=has_con,
            expected="COAP_TYPE_CON used for reliable GET request",
            actual=f"CON={has_con}, NON={has_non}",
            check_type="exact_match",
        )
    )

    # Check 2: Token is set (non-zero length token, common LLM failure: no token)
    has_token = (
        "token" in generated_code.lower()
        and (scoped_contains(generated_code, '0x0', scope='code_only') or scoped_contains(generated_code, '{0x', scope='code_only') or scoped_contains(generated_code, 'token[]', scope='code_only')
             or scoped_contains(generated_code, 'sizeof(token)', scope='code_only') or scoped_contains(generated_code, 'token_len', scope='code_only'))
    )
    details.append(
        CheckDetail(
            check_name="token_set",
            passed=has_token,
            expected="Non-zero token set in CoAP packet",
            actual="present" if has_token else "missing — token may be zero-length",
            check_type="constraint",
        )
    )

    # Check 3: coap_packet_init called before append_option (ordering)
    init_pos = find_in_code(generated_code, "coap_packet_init(")
    opt_pos = find_in_code(generated_code, "coap_packet_append_option(")
    # An option-appending helper defined above the init call site is correct —
    # it cannot run before the caller inits the packet. So the order is only
    # judged where it is actually observable: inside a single function.
    appends_before_init = any(
        "coap_packet_init" in body
        and "coap_packet_append_option" in body
        and body.find("coap_packet_append_option") < body.find("coap_packet_init")
        for _name, body in function_bodies(generated_code)
    )
    order_ok = init_pos != -1 and opt_pos != -1 and not appends_before_init
    details.append(
        CheckDetail(
            check_name="init_before_append_option",
            passed=order_ok,
            expected="coap_packet_init() called before coap_packet_append_option()",
            actual="correct" if order_ok else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 4: Standard CoAP port used (5683)
    has_coap_port = scoped_contains(generated_code, '5683', scope='code_only')
    details.append(
        CheckDetail(
            check_name="coap_standard_port",
            passed=has_coap_port,
            expected="Standard CoAP port 5683 used",
            actual="present" if has_coap_port else "missing — wrong port",
            check_type="exact_match",
        )
    )

    # Check 5: Response parsed with coap_packet_parse
    has_parse = scoped_contains(generated_code, 'coap_packet_parse', scope='code_only')
    details.append(
        CheckDetail(
            check_name="response_parsed",
            passed=has_parse,
            expected="coap_packet_parse() used to parse response",
            actual="present" if has_parse else "missing — response not parsed",
            check_type="exact_match",
        )
    )

    # Check 6: Socket closed after use
    has_close = scoped_contains(generated_code, 'zsock_close', scope='code_only')
    details.append(
        CheckDetail(
            check_name="socket_closed",
            passed=has_close,
            expected="zsock_close() called",
            actual="present" if has_close else "missing — socket leak",
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
