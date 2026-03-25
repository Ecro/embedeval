"""Negative tests for GPIO button interrupt application.

Reference: cases/gpio-basic-001/reference/main.c
Checks:    cases/gpio-basic-001/checks/behavior.py

The reference uses gpio_is_ready_dt() to check both the LED and button devices
before any GPIO operations.

Mutation strategy
-----------------
* missing_device_ready : removes the device-readiness guard entirely.
  The behavior check looks for any of: 'gpio_is_ready_dt', 'device_is_ready',
  'gpio_is_ready' → device_ready_check fails when all three are absent.
"""


def _remove_lines(code: str, pattern: str) -> str:
    """Remove all lines containing *pattern*."""
    return "\n".join(line for line in code.splitlines() if pattern not in line)


NEGATIVES = [
    {
        "name": "missing_device_ready",
        "description": (
            "Device readiness check removed — GPIO operations may crash "
            "if hardware is not yet available"
        ),
        # The reference uses gpio_is_ready_dt; removing it and the surrounding
        # if-block guard leaves no readiness check in the code.
        "mutation": lambda code: (
            code
            # Remove the guard condition line
            .replace(
                "\tif (!gpio_is_ready_dt(&led) || !gpio_is_ready_dt(&button)) {\n\t\treturn -1;\n\t}\n",
                "",
            )
        ),
        "must_fail": ["device_ready_check"],
    },
]
