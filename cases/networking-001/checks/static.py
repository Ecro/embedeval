"""Static analysis checks for MQTT client."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate MQTT code structure."""
    details: list[CheckDetail] = []

    has_mqtt_h = "zephyr/net/mqtt.h" in generated_code
    details.append(
        CheckDetail(
            check_name="mqtt_header",
            passed=has_mqtt_h,
            expected="zephyr/net/mqtt.h included",
            actual="present" if has_mqtt_h else "missing",
            check_type="exact_match",
        )
    )

    has_init = "mqtt_client_init" in generated_code
    details.append(
        CheckDetail(
            check_name="mqtt_client_init",
            passed=has_init,
            expected="mqtt_client_init() called",
            actual="present" if has_init else "missing",
            check_type="exact_match",
        )
    )

    has_connect = "mqtt_connect" in generated_code
    details.append(
        CheckDetail(
            check_name="mqtt_connect_called",
            passed=has_connect,
            expected="mqtt_connect() called",
            actual="present" if has_connect else "missing",
            check_type="exact_match",
        )
    )

    has_publish = "mqtt_publish" in generated_code
    details.append(
        CheckDetail(
            check_name="mqtt_publish_called",
            passed=has_publish,
            expected="mqtt_publish() called",
            actual="present" if has_publish else "missing",
            check_type="exact_match",
        )
    )

    has_evt_handler = "mqtt_evt" in generated_code or "evt_cb" in generated_code
    details.append(
        CheckDetail(
            check_name="event_handler_defined",
            passed=has_evt_handler,
            expected="MQTT event handler defined",
            actual="present" if has_evt_handler else "missing",
            check_type="exact_match",
        )
    )

    return details
