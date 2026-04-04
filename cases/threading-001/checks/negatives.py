"""Negative tests for producer-consumer threading application.

Reference: cases/threading-001/reference/main.c
Checks:    cases/threading-001/checks/behavior.py

The reference:
  - K_THREAD_DEFINE(producer, 1024, producer_entry, NULL, NULL, NULL, 5, 0, 0)
  - K_THREAD_DEFINE(consumer, 1024, consumer_entry, NULL, NULL, NULL, 6, 0, 0)
    Producer priority=5, consumer priority=6 (different) → different_thread_priorities passes.
  - Consumer calls k_msgq_get(&my_msgq, &msg, K_FOREVER) → consumer_blocking_get passes.

Mutation strategy
-----------------
* same_thread_priority : changes consumer priority from 6 to 5 (same as producer).
  The check collects both priority values; len(set(priorities)) == 1 < 2 → fails.

* consumer_no_wait : changes K_FOREVER to K_NO_WAIT in the consumer's msgq_get.
  The check requires K_FOREVER or K_MSEC present alongside k_msgq_get.
  K_NO_WAIT satisfies neither → consumer_blocking_get fails.
"""


def _remove_lines(code: str, pattern: str) -> str:
    """Remove all lines containing *pattern*."""
    return "\n".join(line for line in code.splitlines() if pattern not in line)


NEGATIVES = [
    {
        "name": "same_thread_priority",
        "description": (
            "Consumer priority changed to match producer (both 5) — "
            "equal priorities remove scheduling determinism between threads"
        ),
        # Reference: K_THREAD_DEFINE(consumer, 1024, consumer_entry, NULL, NULL, NULL, 6, 0, 0)
        # Changing the trailing priority argument from 6 to 5 makes both threads equal.
        "mutation": lambda code: code.replace(
            "K_THREAD_DEFINE(consumer, 1024, consumer_entry, NULL, NULL, NULL, 6, 0, 0)",
            "K_THREAD_DEFINE(consumer, 1024, consumer_entry, NULL, NULL, NULL, 5, 0, 0)",
        ),
        "must_fail": ["different_thread_priorities"],
    },
    {
        "name": "consumer_no_wait",
        "description": (
            "Consumer k_msgq_get replaced with k_msgq_peek (non-blocking peek) — "
            "consumer never actually dequeues messages; queue fills and producer stalls"
        ),
        # The consumer_blocking_get check requires k_msgq_get to appear in the
        # code alongside K_FOREVER or K_MSEC. Replacing k_msgq_get with
        # k_msgq_peek removes k_msgq_get from the code entirely; without it
        # both branches of the check fail → consumer_blocking_get fails.
        "mutation": lambda code: code.replace(
            "\t\tif (k_msgq_get(&my_msgq, &msg, K_FOREVER) == 0) {",
            "\t\tif (k_msgq_peek(&my_msgq, &msg) == 0) {",
        ),
        "must_fail": ["consumer_blocking_get"],
    },
    # --- Subtle ---
    {
        "name": "producer_no_sleep",
        "mutation": lambda code: _remove_lines(code, "k_sleep(K_MSEC(100))"),
        "should_fail": ["producer_sleeps_between_sends"],
        "bug_description": "Producer sleep removed — tight send loop starves consumer thread on cooperative schedulers",
    },
]
