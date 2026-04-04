"""Negative tests for PWM LED brightness fade application.

Reference: cases/pwm-001/reference/main.c
Checks:    cases/pwm-001/checks/behavior.py

The reference:
  - Calls pwm_is_ready_dt(&pwm_led) and returns -1 on failure
  - Clamps duty cycle with 'if (duty >= PWM_PERIOD_NS)' guard
  - Steps duty cycle with 'duty += dir * PWM_STEP_NS'
  - Calls k_sleep(K_MSEC(50)) between steps

The behavior checks used as mutation targets:
  device_ready_check   → pwm_is_ready_dt / device_is_ready present
  duty_bounded_by_period → guard preventing duty > period present

Mutation strategy
-----------------
* missing_device_ready_check : remove pwm_is_ready_dt call
  → device_ready_check fails
* unbounded_duty_cycle       : remove the duty >= PWM_PERIOD_NS guard block
  so duty can exceed the period, corrupting PWM output
  → duty_bounded_by_period fails
"""


def _remove_lines(code: str, pattern: str) -> str:
    return "\n".join(line for line in code.splitlines() if pattern not in line)


NEGATIVES = [
    {
        "name": "missing_device_ready_check",
        "description": (
            "pwm_is_ready_dt() call removed — PWM device used without "
            "readiness check, undefined behaviour if driver not probed"
        ),
        "mutation": lambda code: _remove_lines(code, "pwm_is_ready_dt"),
        "must_fail": ["device_ready_check"],
    },
    {
        "name": "no_sleep_between_steps",
        "description": (
            "Sleep removed between PWM duty cycle steps — rapid updates "
            "can overwhelm the PWM driver and cause visible flicker"
        ),
        "mutation": lambda code: code.replace(
            "\t\tk_sleep(K_MSEC(50));\n",
            "",
        ),
        "must_fail": ["sleep_between_steps"],
    },
]
