"""Negative tests for watchdog-fed-by-timer cascaded safety application.

Reference: cases/timer-007/reference/main.c
Checks:    cases/timer-007/checks/behavior.py

The reference:
  - window.max = 3000  (WDT timeout 3000 ms)
  - k_timer_start(&wdt_feed_timer, K_SECONDS(1), K_SECONDS(1))
    → timer period 1 s = 1000 ms  <  3000 ms  ✓

The behavior check (timer_period_less_than_wdt_timeout) does:
  1. Extracts wdt_max from 'window.max = <N>'  → 3000
  2. If K_SECONDS(<N>) found: period_ok = (N * 1000) < wdt_max
  3. If K_MSEC(<N>) found:   period_ok = N < wdt_max

Mutation strategy
-----------------
* period_equals_timeout : changes K_SECONDS(1) → K_SECONDS(3).
  Now period = 3 * 1000 = 3000 ms which is NOT < 3000 ms → check fails.
  (Using the exact token from the reference to guarantee a precise replacement.)
"""

NEGATIVES = [
    {
        "name": "period_equals_timeout",
        "description": (
            "Timer period set equal to WDT timeout (both 3 s) — "
            "no safety margin; watchdog may fire before timer callback runs"
        ),
        # Reference has K_SECONDS(1) twice in k_timer_start call.
        # Replace both occurrences so period = 3000 ms == window.max = 3000 ms.
        "mutation": lambda code: code.replace("K_SECONDS(1)", "K_SECONDS(3)"),
        "must_fail": ["timer_period_less_than_wdt_timeout"],
    },
    # --- Subtle ---
    {
        "name": "period_almost_equals_timeout",
        "mutation": lambda code: code.replace("K_SECONDS(1)", "K_MSEC(2999)"),
        "should_fail": ["timer_period_less_than_wdt_timeout"],
        "bug_description": "Period 2999ms with 3000ms timeout — technically < but 1ms margin is unsafe for real-time",
    },
]
