"""Negative tests for GPIO interrupt debounce with timer application.

Reference: cases/gpio-basic-006/reference/main.c
Checks:    cases/gpio-basic-006/checks/behavior.py

The reference:
  - ISR calls k_timer_start(&debounce_tmr, K_MSEC(50), K_NO_WAIT)
  - main() checks gpio_is_ready_dt(&led) || gpio_is_ready_dt(&button)

The behavior checks used as mutation targets:
  isr_starts_timer    → k_timer_start present anywhere in code
  device_ready_checks → gpio_is_ready_dt / device_is_ready present

Mutation strategy
-----------------
* isr_reads_gpio_directly : replace k_timer_start call in ISR with a direct
  gpio_pin_get_dt call — debounce pattern broken, ISR does GPIO read directly
  → isr_starts_timer fails
* missing_device_ready_checks : remove gpio_is_ready_dt call
  → device_ready_checks fails
"""


def _remove_lines(code: str, pattern: str) -> str:
    return "\n".join(line for line in code.splitlines() if pattern not in line)


NEGATIVES = [
    {
        "name": "isr_reads_gpio_directly",
        "description": (
            "k_timer_start removed from ISR — ISR reads GPIO pin directly "
            "instead of deferring to a timer; contact bounce causes spurious "
            "LED toggles"
        ),
        "mutation": lambda code: code.replace(
            "k_timer_start(&debounce_tmr, K_MSEC(50), K_NO_WAIT);",
            "gpio_pin_toggle_dt(&led); /* broken: no debounce */",
        ),
        "must_fail": ["isr_starts_timer"],
    },
    {
        "name": "missing_device_ready_checks",
        "description": (
            "gpio_is_ready_dt() call removed — GPIO devices used without "
            "readiness check; fails silently on unprobed hardware"
        ),
        "mutation": lambda code: _remove_lines(code, "gpio_is_ready_dt"),
        "must_fail": ["device_ready_checks"],
    },
]
