"""Negative tests for periodic kernel timer application.

Reference: cases/timer-001/reference/main.c
Checks:    cases/timer-001/checks/behavior.py

The reference:
  - Declares 'static volatile int counter' (ISR-safe access)
  - Calls k_timer_start(&my_timer, K_MSEC(500), K_MSEC(500))

Mutation strategy
-----------------
* missing_volatile : removes the 'volatile' qualifier from the counter
  declaration. The check_qualifier_on_variable helper looks for the
  qualifier immediately before the variable name in the declaration —
  removing it causes counter_is_volatile to fail.

* wrong_timer_period : changes K_MSEC(500) to K_MSEC(100). The check
  looks for the regex K_MSEC\\s*\\(\\s*500\\s*\\); with 100 there the
  timer_period_500ms check fails.
"""


def _remove_lines(code: str, pattern: str) -> str:
    """Remove all lines containing *pattern*."""
    return "\n".join(line for line in code.splitlines() if pattern not in line)


NEGATIVES = [
    {
        "name": "missing_volatile",
        "description": (
            "volatile qualifier removed from counter — ISR and main thread "
            "may see stale cached values, leading to incorrect counts"
        ),
        # Reference line: "static volatile int counter;"
        # Removing 'volatile ' leaves a plain int, which fails counter_is_volatile.
        "mutation": lambda code: code.replace("static volatile int counter", "static int counter"),
        "must_fail": ["counter_is_volatile"],
    },
    {
        "name": "wrong_timer_period",
        "description": (
            "Timer period changed from 500 ms to 100 ms — violates the "
            "specification requirement of a 500 ms periodic timer"
        ),
        # Reference: k_timer_start(&my_timer, K_MSEC(500), K_MSEC(500))
        # Replacing 500 → 100 means K_MSEC(500) is absent → timer_period_500ms fails.
        "mutation": lambda code: code.replace("K_MSEC(500)", "K_MSEC(100)"),
        "must_fail": ["timer_period_500ms"],
    },
    # --- Subtle ---
    {
        "name": "counter_not_incremented",
        "mutation": lambda code: code.replace("counter++", "counter = 0"),
        "should_fail": ["expiry_increments_counter"],
        "bug_description": "Counter reset to 0 instead of incremented — timer fires but counter never grows",
    },
]
