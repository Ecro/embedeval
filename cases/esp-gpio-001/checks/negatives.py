"""Negative tests for ESP-IDF GPIO blink application.

Reference: cases/esp-gpio-001/reference/main.c
Checks:    cases/esp-gpio-001/checks/static.py  (no_zephyr_apis)
           cases/esp-gpio-001/checks/behavior.py (vtaskdelay_used)

The reference uses only ESP-IDF APIs (gpio_config, gpio_set_level, vTaskDelay).

Mutation strategy
-----------------
* zephyr_api_hallucination : inserts a '#include <zephyr/kernel.h>' line and a
  call to k_sleep() — both are in the Zephyr API list checked by the static module.
  'k_sleep' appears in 'zephyr_apis' list → no_zephyr_apis fails.

* busy_wait_instead_of_delay : comments out the vTaskDelay call.
  The behavior check looks for the literal string 'vTaskDelay' → vtaskdelay_used fails.
"""


def _remove_lines(code: str, pattern: str) -> str:
    """Remove all lines containing *pattern*."""
    return "\n".join(line for line in code.splitlines() if pattern not in line)


NEGATIVES = [
    {
        "name": "zephyr_api_hallucination",
        "description": "Zephyr k_sleep API injected into ESP-IDF code — wrong platform",
        # The static check's zephyr_apis list includes 'k_sleep'.
        # Prepend the include and add a k_sleep call so the check fires.
        "mutation": lambda code: (
            '#include <zephyr/kernel.h>\n'
            + code.replace(
                "void app_main(void)",
                "void app_main(void) /* k_sleep(K_MSEC(1)); */\n"
                "void app_main(void)",
                1,
            ).replace(
                "void app_main(void) /* k_sleep(K_MSEC(1)); */\nvoid app_main(void)",
                "void app_main(void)",
                1,
            )
            # Simpler: just prepend the include which contains 'zephyr/' in path
            # AND add k_sleep literal so both 'k_sleep' and header are present.
        ).replace(
            "vTaskDelay(pdMS_TO_TICKS(500));",
            "vTaskDelay(pdMS_TO_TICKS(500)); k_sleep(K_MSEC(500));",
        ),
        "must_fail": ["no_zephyr_apis"],
    },
    {
        "name": "busy_wait_instead_of_delay",
        "description": "vTaskDelay removed — CPU spins in busy-wait, starving other tasks",
        "mutation": lambda code: _remove_lines(code, "vTaskDelay"),
        "must_fail": ["vtaskdelay_used"],
    },
    # --- Subtle ---
    {
        "name": "busy_wait_for_loop",
        "mutation": lambda code: code.replace(
            "vTaskDelay(pdMS_TO_TICKS(500));",
            "for(volatile int _d=0; _d<5000000; _d++); /* busy wait */"
        ),
        "should_fail": ["vtaskdelay_used"],
        "bug_description": "CPU busy-wait loop instead of OS delay — 100% CPU, no other tasks can run",
    },
]
