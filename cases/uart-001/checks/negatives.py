"""Negative tests for UART poll echo application.

Reference: cases/uart-001/reference/main.c
Checks:    cases/uart-001/checks/behavior.py

The reference:
  - Calls device_is_ready(uart_dev) and returns -1 on failure
  - Polls with uart_poll_in and only echoes when return == 0
  - Runs in a while(1) loop

The behavior checks used as mutation targets:
  device_ready_check     → device_is_ready / uart_is_ready present
  poll_in_return_checked → uart_poll_in result used in conditional

Mutation strategy
-----------------
* missing_device_ready_check : remove device_is_ready call
  → device_ready_check fails
* unconditional_echo         : remove if (uart_poll_in(...) == 0) conditional
  guard so uart_poll_out is called regardless of poll result
  → poll_in_return_checked fails
"""


def _remove_lines(code: str, pattern: str) -> str:
    return "\n".join(line for line in code.splitlines() if pattern not in line)


NEGATIVES = [
    {
        "name": "missing_device_ready_check",
        "description": (
            "device_is_ready() call removed — UART device used without "
            "readiness check, causing undefined behaviour on unprobed hardware"
        ),
        "mutation": lambda code: _remove_lines(code, "device_is_ready"),
        "must_fail": ["device_ready_check"],
    },
    {
        "name": "unconditional_echo",
        "description": (
            "uart_poll_in return value not checked — uart_poll_out called "
            "even when no byte is available, sending garbage characters"
        ),
        # Replace the conditional echo with an unconditional one:
        # remove the 'if (uart_poll_in(uart_dev, &c) == 0)' guard, keeping
        # the poll call but dropping the '== 0' check so the code reads:
        #   uart_poll_in(uart_dev, &c);
        #   uart_poll_out(uart_dev, c);
        "mutation": lambda code: code.replace(
            "if (uart_poll_in(uart_dev, &c) == 0) {\n\t\t\tuart_poll_out(uart_dev, c);\n\t\t}",
            "uart_poll_in(uart_dev, &c);\n\t\tuart_poll_out(uart_dev, c);",
        ),
        "must_fail": ["poll_in_return_checked"],
    },
]
