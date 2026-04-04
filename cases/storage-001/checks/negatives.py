"""Negative tests for NVS key-value store.

Reference: cases/storage-001/reference/main.c
Checks:    cases/storage-001/checks/behavior.py

The reference:
  - calls nvs_mount() first, then nvs_write(), then nvs_read()
  - mount_before_io check verifies mount_pos < write_pos and mount_pos < read_pos
  - write_before_read check verifies write_pos < read_pos

Mutation strategy
-----------------
* mount_after_write : swaps nvs_mount and nvs_write so mount comes after the
  write attempt.  The check mount_before_io will fail because mount_pos > write_pos.

* read_before_write : removes nvs_write so only nvs_read remains.
  The check write_before_read will fail because write_pos == -1.
"""


def _remove_lines(code: str, pattern: str) -> str:
    return "\n".join(line for line in code.splitlines() if pattern not in line)


NEGATIVES = [
    {
        "name": "mount_after_write",
        "description": (
            "nvs_write() called before nvs_mount() — NVS filesystem is not "
            "initialised; write will fail or corrupt flash"
        ),
        # Swap the order: move the mount block after the write block.
        # Simplest reliable mutation: insert a fake write line before mount.
        "mutation": lambda code: code.replace(
            "\tret = nvs_mount(&fs);",
            "\t/* BUG: mount moved after write */\n\tret = nvs_write(&fs, NVS_ID, &write_val, sizeof(write_val));\n\t(void)ret;\n\tret = nvs_mount(&fs);",
        ).replace(
            # Remove the original nvs_write so it only appears once (before mount now)
            "\tret = nvs_write(&fs, NVS_ID, &write_val, sizeof(write_val));\n\tif (ret < 0) {\n\t\tprintk(\"NVS write failed: %d\\n\", ret);\n\t\treturn ret;\n\t}",
            "\t/* nvs_write moved above */",
        ),
        "must_fail": ["mount_before_io"],
    },
    {
        "name": "read_before_write",
        "description": (
            "nvs_write() removed — data is read before ever being written; "
            "NVS will return stale or uninitialised values"
        ),
        "mutation": lambda code: _remove_lines(code, "nvs_write"),
        "must_fail": ["write_before_read"],
    },
]
