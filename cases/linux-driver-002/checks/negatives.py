"""Negative tests for Linux platform driver with Device Tree binding.

Reference: cases/linux-driver-002/reference/main.c
Checks:    cases/linux-driver-002/checks/behavior.py

The reference:
  - of_device_id table ends with {} sentinel entry
  - MODULE_DEVICE_TABLE(of, mydev_of_match) present for auto-load

The behavior checks used as mutation targets:
  of_match_table_sentinel → {} sentinel at end of of_device_id array
  module_device_table_of  → MODULE_DEVICE_TABLE(of, ...) present

Mutation strategy
-----------------
* missing_sentinel      : replace the {} sentinel with a garbage entry
  → of_match_table_sentinel fails (kernel may walk off end of table)
* missing_device_table  : remove MODULE_DEVICE_TABLE line
  → module_device_table_of fails (driver not auto-loaded by udev)
"""


def _remove_lines(code: str, pattern: str) -> str:
    return "\n".join(line for line in code.splitlines() if pattern not in line)


NEGATIVES = [
    {
        "name": "missing_sentinel",
        "description": (
            "of_device_id table {} sentinel removed — kernel walks off the "
            "end of the match table, causing a crash or silent mismatch"
        ),
        # Replace the terminating sentinel line with nothing.
        # Reference has: '\t{},\n' as the last entry before '};'
        "mutation": lambda code: code.replace("\t{},\n", ""),
        "must_fail": ["of_match_table_sentinel"],
    },
    {
        "name": "missing_device_table",
        "description": (
            "MODULE_DEVICE_TABLE(of, ...) removed — udev cannot match the "
            "device to this module; driver never auto-loads"
        ),
        "mutation": lambda code: _remove_lines(code, "MODULE_DEVICE_TABLE"),
        "must_fail": ["module_device_table_of"],
    },
]
