"""Behavioral checks for CoAP client GET request."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate CoAP client behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: CON message type used (reliable delivery), not NON
    has_con = "COAP_TYPE_CON" in generated_code
    has_non = "COAP_TYPE_NON" in generated_code
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
        and ("0x0" in generated_code or "{0x" in generated_code or "token[]" in generated_code
             or "sizeof(token)" in generated_code or "token_len" in generated_code)
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
    init_pos = generated_code.find("coap_packet_init")
    opt_pos = generated_code.find("coap_packet_append_option")
    order_ok = init_pos != -1 and opt_pos != -1 and init_pos < opt_pos
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
    has_coap_port = "5683" in generated_code
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
    has_parse = "coap_packet_parse" in generated_code
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
    has_close = "zsock_close" in generated_code
    details.append(
        CheckDetail(
            check_name="socket_closed",
            passed=has_close,
            expected="zsock_close() called",
            actual="present" if has_close else "missing — socket leak",
            check_type="exact_match",
        )
    )

    return details
