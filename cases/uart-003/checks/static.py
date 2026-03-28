"""Static analysis checks for multi-UART runtime baudrate change application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate multi-UART code structure and required elements."""
    details: list[CheckDetail] = []

    # Check 1: Includes zephyr/drivers/uart.h
    has_uart_h = "zephyr/drivers/uart.h" in generated_code
    details.append(
        CheckDetail(
            check_name="uart_header_included",
            passed=has_uart_h,
            expected="zephyr/drivers/uart.h included",
            actual="present" if has_uart_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: Includes zephyr/kernel.h
    has_kernel_h = "zephyr/kernel.h" in generated_code
    details.append(
        CheckDetail(
            check_name="kernel_header_included",
            passed=has_kernel_h,
            expected="zephyr/kernel.h included",
            actual="present" if has_kernel_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: Uses uart_configure() for baudrate setup
    has_uart_configure = "uart_configure" in generated_code
    details.append(
        CheckDetail(
            check_name="uart_configure_called",
            passed=has_uart_configure,
            expected="uart_configure() called with struct uart_config",
            actual="present" if has_uart_configure else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Both uart0 and uart1 referenced
    has_uart0 = "uart0" in generated_code
    has_uart1 = "uart1" in generated_code
    has_both = has_uart0 and has_uart1
    details.append(
        CheckDetail(
            check_name="both_uarts_referenced",
            passed=has_both,
            expected="Both uart0 and uart1 used",
            actual=f"uart0={has_uart0}, uart1={has_uart1}",
            check_type="exact_match",
        )
    )

    # Check 5: struct uart_config used
    has_uart_cfg_struct = "uart_config" in generated_code
    details.append(
        CheckDetail(
            check_name="uart_config_struct_used",
            passed=has_uart_cfg_struct,
            expected="struct uart_config used for configuration",
            actual="present" if has_uart_cfg_struct else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: Buffer check — RX buffer size > 0 if any buffer declared
    import re
    # Any char/uint8_t buffer must have non-zero size
    buf_matches = re.findall(r"(?:char|uint8_t)\s+\w+\[(\d+)\]", generated_code)
    all_nonzero = all(int(s) > 0 for s in buf_matches)
    details.append(
        CheckDetail(
            check_name="rx_buffer_size_nonzero",
            passed=all_nonzero,
            expected="Any declared buffers have positive size",
            actual="ok" if all_nonzero else "zero-sized buffer found",
            check_type="constraint",
        )
    )

    return details
