"""Negative tests for Zephyr sensor API temperature read.

Reference: cases/sensor-driver-001/reference/main.c
Checks:    cases/sensor-driver-001/checks/behavior.py

The reference:
  - Calls sensor_sample_fetch(dev) THEN sensor_channel_get(dev, ..., &temp).
    The check finds each function's position; fetch_pos < get_pos → fetch_before_get passes.
  - Checks 'ret < 0' after both sensor API calls → sensor_error_handling passes.

Mutation strategy
-----------------
* get_before_fetch : swaps the two sensor API call lines so channel_get appears
  before sample_fetch. The check compares string positions; after the swap
  get_pos < fetch_pos → fetch_before_get fails.

* missing_error_handling : removes all lines that check the return value after
  sensor API calls (lines containing 'if (ret < 0)'). The has_error_check helper
  looks for 'ret < 0', '< 0', '!= 0' patterns; with them gone → sensor_error_handling fails.
"""


def _remove_lines(code: str, pattern: str) -> str:
    """Remove all lines containing *pattern*."""
    return "\n".join(line for line in code.splitlines() if pattern not in line)


NEGATIVES = [
    {
        "name": "get_before_fetch",
        "description": (
            "sensor_channel_get called before sensor_sample_fetch — reads "
            "stale or uninitialized sensor data from the driver buffer"
        ),
        # The check compares: fetch_pos != -1 and get_pos != -1 and fetch_pos < get_pos.
        # Replacing the fetch call line with a second get call makes sensor_sample_fetch
        # absent (fetch_pos == -1), so the first condition fails → fetch_before_get fails.
        "mutation": lambda code: code.replace(
            "\t\tret = sensor_sample_fetch(dev);\n",
            "\t\tret = sensor_channel_get(dev, SENSOR_CHAN_AMBIENT_TEMP, &temp); /* BUG: skipped fetch */\n",
            1,
        ),
        "must_fail": ["fetch_before_get"],
    },
    {
        "name": "missing_error_handling",
        "description": (
            "Error checks on sensor_sample_fetch and sensor_channel_get removed — "
            "failures are silently ignored and stale data is printed as valid"
        ),
        # Remove all lines containing 'if (ret < 0)' — this removes both error checks
        # in the sensor loop. The device-ready guard uses 'return -ENODEV' (no 'ret < 0')
        # so it is not affected. After removal, has_error_check (which looks for
        # 'ret < 0' patterns) finds nothing → sensor_error_handling fails.
        "mutation": lambda code: _remove_lines(code, "if (ret < 0)"),
        "must_fail": ["sensor_error_handling"],
    },
    # --- Subtle ---
    {
        "name": "missing_device_ready",
        "mutation": lambda code: _remove_lines(code, "device_is_ready"),
        "should_fail": ["device_ready_check"],
        "bug_description": "device_is_ready() guard removed — sensor operations proceed even when driver not initialised",
    },
]
