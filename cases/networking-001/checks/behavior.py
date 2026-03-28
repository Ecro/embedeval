"""Behavioral checks for MQTT client."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate MQTT behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: Both connect and publish present
    # (ordering enforced by program logic — connect in main, publish after)
    has_connect = "mqtt_connect" in generated_code
    has_publish = "mqtt_publish" in generated_code
    details.append(
        CheckDetail(
            check_name="connect_and_publish_present",
            passed=has_connect and has_publish,
            expected="Both mqtt_connect() and mqtt_publish() present",
            actual=f"connect={has_connect}, publish={has_publish}",
            check_type="constraint",
        )
    )

    # Check 2: Event handler covers CONNACK
    has_connack = "MQTT_EVT_CONNACK" in generated_code
    details.append(
        CheckDetail(
            check_name="handles_connack",
            passed=has_connack,
            expected="MQTT_EVT_CONNACK handled in event callback",
            actual="present" if has_connack else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: mqtt_input/mqtt_live in loop
    # (LLM failure: not calling mqtt_input for protocol processing)
    has_input = "mqtt_input" in generated_code
    has_live = "mqtt_live" in generated_code
    details.append(
        CheckDetail(
            check_name="protocol_loop",
            passed=has_input and has_live,
            expected="mqtt_input() and mqtt_live() in main loop",
            actual=f"input={has_input}, live={has_live}",
            check_type="constraint",
        )
    )

    # Check 4: Topic string defined (not empty)
    has_topic = (
        "topic" in generated_code.lower()
        and ('"test/' in generated_code or "topic" in generated_code)
    )
    details.append(
        CheckDetail(
            check_name="topic_defined",
            passed=has_topic,
            expected="MQTT topic string defined",
            actual="present" if has_topic else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Error handling on connect
    has_conn_err = "< 0" in generated_code
    details.append(
        CheckDetail(
            check_name="connect_error_handling",
            passed=has_conn_err,
            expected="Error check on mqtt_connect return",
            actual="present" if has_conn_err else "missing",
            check_type="constraint",
        )
    )

    # Check 6: Client ID set
    has_client_id = "client_id" in generated_code
    details.append(
        CheckDetail(
            check_name="client_id_set",
            passed=has_client_id,
            expected="MQTT client_id configured",
            actual="present" if has_client_id else "missing",
            check_type="exact_match",
        )
    )

    # Check 7: Port number in network byte order (htons)
    has_htons = bool(re.search(r'htons\s*\(', generated_code))
    details.append(
        CheckDetail(
            check_name="port_byte_order",
            passed=has_htons,
            expected="htons() used for port number (network byte order)",
            actual="htons found" if has_htons else "no htons for port",
            check_type="constraint",
        )
    )

    return details
