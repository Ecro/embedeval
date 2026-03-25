"""Negative tests for watchdog with multi-thread health monitoring.

Reference: cases/watchdog-005/reference/main.c
Checks:    cases/watchdog-005/checks/behavior.py

The reference:
  - Declares: static volatile int worker_alive;
  - Worker sets worker_alive = 1 in a while(1) loop.
  - Monitor checks 'if (worker_alive)' then resets it to 0 and calls wdt_feed().

The behavior check (wdt_feed_is_conditional) uses a regex that looks for:
    if (<pattern matching alive/health/flag/worker>) ... wdt_feed
If wdt_feed appears unconditionally (not guarded by such an if), the check fails.

Mutation strategy
-----------------
* unconditional_feed : replaces the conditional guard with an always-true condition.
  The regex in wdt_feed_is_conditional requires the if-expression to contain
  words like 'alive', 'health', 'flag', or 'worker'.  Replacing 'worker_alive'
  with a literal '1' in the condition means none of those keywords appear in the
  if-expression → wdt_feed_is_conditional fails.
"""

NEGATIVES = [
    {
        "name": "unconditional_feed",
        "description": (
            "WDT fed unconditionally (always-true guard) instead of checking worker health — "
            "defeats the purpose; a stalled worker will not trigger a reset"
        ),
        # Replace 'if (worker_alive)' with 'if (1)' so the guard keyword is gone.
        # The regex r"if\s*\([^)]*(?:alive|health|flag|worker)[^)]*\)" will no longer match.
        "mutation": lambda code: code.replace("if (worker_alive)", "if (1) /* always feed */"),
        "must_fail": ["wdt_feed_is_conditional"],
    },
]
