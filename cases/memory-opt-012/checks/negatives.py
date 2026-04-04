"""Negative tests for flash-efficient CRC-16 implementation.

Reference: cases/memory-opt-012/reference/main.c
Checks:    cases/memory-opt-012/checks/behavior.py

The reference:
  - Uses only integer types (uint8_t, uint16_t) — no float/double
  - Has no large string literals (>50 chars)

The behavior checks used as mutation targets:
  no_floating_point    → no float / double keyword in stripped code
  no_large_string_literals → no string literal >= 50 chars

Mutation strategy
-----------------
* adds_floating_point  : inject a float variable into the CRC function
  → no_floating_point fails (float keyword triggers the regex)
* adds_large_string    : inject a long debug string literal
  → no_large_string_literals fails (>50 chars in a string)
"""

NEGATIVES = [
    {
        "name": "adds_floating_point",
        "description": (
            "float variable added to CRC function — Cortex-M0 lacks FPU; "
            "soft-float library routines bloat flash by several kB"
        ),
        # Insert a float declaration just after the opening brace of crc16_ccitt.
        # The reference has 'uint16_t crc = CRC16_CCITT_INIT;' as first line in body.
        "mutation": lambda code: code.replace(
            "    uint16_t crc = CRC16_CCITT_INIT;",
            "    float scale = 1.0f; /* unnecessary FP */\n    uint16_t crc = CRC16_CCITT_INIT;",
        ),
        "must_fail": ["no_floating_point"],
    },
    {
        "name": "adds_large_string_literal",
        "description": (
            "Long debug string literal added — string constants live in flash; "
            "a 60+ char string wastes precious flash on a constrained MCU"
        ),
        # Inject an over-50-char string via printk right before the existing printk.
        "mutation": lambda code: code.replace(
            '    printk("CRC-16-CCITT: 0x%04X\\n", result);',
            '    printk("DEBUG: Running CRC-16-CCITT computation on test buffer data\\n");\n    printk("CRC-16-CCITT: 0x%04X\\n", result);',
        ),
        "must_fail": ["no_large_string_literals"],
    },
]
