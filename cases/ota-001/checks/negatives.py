"""Negative tests for OTA image confirmation.

Reference: cases/ota-001/reference/main.c
Checks:    cases/ota-001/checks/behavior.py

The reference:
  - calls boot_is_img_confirmed() first, then self_test(), then
    boot_write_img_confirmed() — all inside a conditional block
  - check_before_confirm requires boot_is_img_confirmed pos < boot_write_img_confirmed pos
  - self_test_before_confirm requires self_test() pos < boot_write_img_confirmed pos

Mutation strategy
-----------------
* confirm_without_check : removes boot_is_img_confirmed() call entirely.
  The check check_before_confirm will fail (check_pos == -1).

* confirm_without_self_test : removes the self_test() call and its conditional.
  The check self_test_before_confirm will fail (self_test_pos == -1).
"""


def _remove_lines(code: str, pattern: str) -> str:
    return "\n".join(line for line in code.splitlines() if pattern not in line)


NEGATIVES = [
    {
        "name": "confirm_without_check",
        "description": (
            "boot_is_img_confirmed() removed — image is confirmed on every boot "
            "without checking whether it is already confirmed; swap state corruption risk"
        ),
        "mutation": lambda code: _remove_lines(code, "boot_is_img_confirmed"),
        "must_fail": ["check_before_confirm"],
    },
    {
        "name": "confirm_without_self_test",
        "description": (
            "self_test() call removed — image is confirmed without running "
            "any validation; a faulty firmware update will be permanently committed"
        ),
        "mutation": lambda code: _remove_lines(
            _remove_lines(code, "self_test"), "Self-test"
        ),
        "must_fail": ["self_test_before_confirm"],
    },
]
