"""Negative tests for MQTT client.

Reference: cases/networking-001/reference/main.c
Checks:    cases/networking-001/checks/behavior.py

The reference:
  - calls mqtt_connect() then enters a loop calling mqtt_input() + mqtt_live()
  - handles MQTT_EVT_CONNACK in the event callback

Mutation strategy
-----------------
* no_protocol_loop : removes mqtt_input and mqtt_live calls.
  The check protocol_loop requires both present — will fail.

* no_connack_handler : removes the MQTT_EVT_CONNACK case from the switch.
  The check handles_connack looks for "MQTT_EVT_CONNACK" — will fail.
"""


def _remove_lines(code: str, pattern: str) -> str:
    return "\n".join(line for line in code.splitlines() if pattern not in line)


NEGATIVES = [
    {
        "name": "no_protocol_loop",
        "description": (
            "mqtt_input() and mqtt_live() removed from main loop — MQTT "
            "protocol processing stalls; no keepalive, no incoming events"
        ),
        "mutation": lambda code: _remove_lines(
            _remove_lines(code, "mqtt_input"), "mqtt_live"
        ),
        "must_fail": ["protocol_loop"],
    },
    {
        "name": "no_connack_handler",
        "description": (
            "MQTT_EVT_CONNACK case removed from event handler — broker "
            "acknowledgement is silently ignored and connected flag never set"
        ),
        "mutation": lambda code: _remove_lines(code, "MQTT_EVT_CONNACK"),
        "must_fail": ["handles_connack"],
    },
]
