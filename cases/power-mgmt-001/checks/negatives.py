"""Negative tests for PM device action handler.

Reference: cases/power-mgmt-001/reference/main.c
Checks:    cases/power-mgmt-001/checks/behavior.py

The reference switch has three arms:
  case PM_DEVICE_ACTION_SUSPEND: ... return 0;
  case PM_DEVICE_ACTION_RESUME:  ... return 0;
  default:                        return -ENOTSUP;

The reference also calls pm_device_action_run for both SUSPEND and RESUME.

Mutation strategy
-----------------
* missing_default_enotsup : removes both the 'default:' case and the ENOTSUP
  return from the switch. The unsupported_action_error check requires either
  ENOTSUP in the code OR a default/else keyword — with both removed it fails.

* missing_resume_case : removes every line that contains PM_DEVICE_ACTION_RESUME
  (both the switch case and the pm_device_action_run call). The
  both_transitions_handled check requires PM_DEVICE_ACTION_RESUME to appear in
  stripped code → fails when all occurrences are removed.
"""


def _remove_lines(code: str, pattern: str) -> str:
    """Remove all lines containing *pattern*."""
    return "\n".join(line for line in code.splitlines() if pattern not in line)


NEGATIVES = [
    {
        "name": "missing_default_enotsup",
        "description": (
            "Default case and -ENOTSUP return removed from PM action switch — "
            "unknown PM actions silently succeed instead of returning an error"
        ),
        # Remove the entire 'default:\n\t\treturn -ENOTSUP;\n' block from the switch.
        # After removal: no ENOTSUP token, no 'default' keyword → unsupported_action_error fails.
        "mutation": lambda code: code.replace(
            "\tdefault:\n\t\treturn -ENOTSUP;\n\t}",
            "\t}",
        ),
        "must_fail": ["unsupported_action_error"],
    },
    {
        "name": "missing_resume_case",
        "description": (
            "PM_DEVICE_ACTION_RESUME case and pm_device_action_run(RESUME) call "
            "removed — device can be suspended but never resumed"
        ),
        # _remove_lines deletes every line containing PM_DEVICE_ACTION_RESUME,
        # which covers the switch case label and the pm_device_action_run call.
        # After removal: has_resume=False → both_transitions_handled fails.
        "mutation": lambda code: _remove_lines(code, "PM_DEVICE_ACTION_RESUME"),
        "must_fail": ["both_transitions_handled"],
    },
    # --- Subtle ---
    {
        "name": "missing_suspend_case",
        "mutation": lambda code: _remove_lines(code, "PM_DEVICE_ACTION_SUSPEND"),
        "should_fail": ["both_transitions_handled"],
        "bug_description": "SUSPEND case removed — device state machine is incomplete; only resume handled",
    },
]
