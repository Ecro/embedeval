"""Static analysis checks for MQTT with Last Will and Testament."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate MQTT LWT code structure."""
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

    has_will_topic = "will_topic" in generated_code
    details.append(
        CheckDetail(
            check_name="will_topic_configured",
            passed=has_will_topic,
            expected="client.will_topic configured",
            actual="present" if has_will_topic else "missing — LWT topic not set",
            check_type="exact_match",
        )
    )

    has_will_message = "will_message" in generated_code
    details.append(
        CheckDetail(
            check_name="will_message_configured",
            passed=has_will_message,
            expected="client.will_message configured",
            actual="present" if has_will_message else "missing — LWT message not set",
            check_type="exact_match",
        )
    )

    has_will_qos = "will_message.topic.qos" in generated_code or "MQTT_QOS" in generated_code
    details.append(
        CheckDetail(
            check_name="will_qos_set",
            passed=has_will_qos,
            expected="Will message QoS set",
            actual="present" if has_will_qos else "missing — QoS not configured for LWT",
            check_type="exact_match",
        )
    )

    has_mqtt_connect = "mqtt_connect" in generated_code
    details.append(
        CheckDetail(
            check_name="mqtt_connect_called",
            passed=has_mqtt_connect,
            expected="mqtt_connect() called",
            actual="present" if has_mqtt_connect else "missing",
            check_type="exact_match",
        )
    )

    # Hallucination: mosquitto_* APIs are not Zephyr
    uses_mosquitto = "mosquitto_" in generated_code
    details.append(
        CheckDetail(
            check_name="no_mosquitto_api",
            passed=not uses_mosquitto,
            expected="mosquitto_* API NOT used (not available in Zephyr)",
            actual="clean" if not uses_mosquitto else "HALLUCINATION: mosquitto_* API is not Zephyr",
            check_type="exact_match",
        )
    )

    return details
