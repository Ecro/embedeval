"""Negative tests for BLE central (scan + connect + GATT discover).

Reference: cases/ble-008/reference/main.c
Checks:    cases/ble-008/checks/behavior.py

The reference:
  - Calls bt_conn_unref(default_conn) inside the 'disconnected' callback.
  - Uses only Zephyr BLE APIs (bt_le_scan_start, bt_conn_le_create, bt_gatt_discover).

Mutation strategy
-----------------
* missing_conn_unref   : removes the bt_conn_unref line inside disconnected().
  The behavior check searches for bt_conn_unref after the position of the
  'disconnected' function definition → conn_unref_in_disconnected fails.

* cross_platform_api   : prepends an ESP-IDF BLE include and an esp_ble_gap_ call.
  check_no_cross_platform_apis skips POSIX and Linux_Userspace but not ESP-IDF;
  _BLE_HALLUCINATED_APIS list includes 'esp_ble_gap_'; both checks look for these
  in the code → no_cross_platform_ble_apis fails.
"""


def _remove_lines(code: str, pattern: str) -> str:
    """Remove all lines containing *pattern*."""
    return "\n".join(line for line in code.splitlines() if pattern not in line)


NEGATIVES = [
    {
        "name": "missing_conn_unref",
        "description": "bt_conn_unref() missing from disconnected callback — connection reference leaked",
        "mutation": lambda code: _remove_lines(code, "bt_conn_unref"),
        "must_fail": ["conn_unref_in_disconnected"],
    },
    {
        "name": "cross_platform_api",
        "description": "ESP-IDF BLE API injected into Zephyr code — cross-platform hallucination",
        # Append a call to esp_ble_gap_start_scanning which is in _BLE_HALLUCINATED_APIS
        # as the prefix 'esp_ble_gap_'.
        "mutation": lambda code: (
            code + '\n/* hallucination */\nvoid bad(void) { esp_ble_gap_start_scanning(10); }\n'
        ),
        "must_fail": ["no_cross_platform_ble_apis"],
    },
]
