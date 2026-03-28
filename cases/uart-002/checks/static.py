"""Static analysis checks for UART async API with DMA application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate UART async code structure and required elements."""
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

    # Check 3: Uses uart_callback_set (async API, not polling)
    has_callback_set = "uart_callback_set" in generated_code
    details.append(
        CheckDetail(
            check_name="uses_uart_callback_set",
            passed=has_callback_set,
            expected="uart_callback_set() used (async API)",
            actual="present" if has_callback_set else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Uses uart_tx (async transmit)
    has_uart_tx = "uart_tx" in generated_code
    details.append(
        CheckDetail(
            check_name="uses_uart_tx",
            passed=has_uart_tx,
            expected="uart_tx() used for async transmit",
            actual="present" if has_uart_tx else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Uses uart_rx_enable
    has_rx_enable = "uart_rx_enable" in generated_code
    details.append(
        CheckDetail(
            check_name="uses_uart_rx_enable",
            passed=has_rx_enable,
            expected="uart_rx_enable() called to enable async RX",
            actual="present" if has_rx_enable else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: Hallucination — uart_read() and uart_write() do not exist in Zephyr
    has_fake_read = "uart_read(" in generated_code
    has_fake_write = "uart_write(" in generated_code
    has_hallucination = has_fake_read or has_fake_write
    details.append(
        CheckDetail(
            check_name="no_uart_read_write_hallucination",
            passed=not has_hallucination,
            expected="uart_read()/uart_write() not used (not Zephyr APIs)",
            actual="hallucinated API found" if has_hallucination else "clean",
            check_type="constraint",
        )
    )

    # Check 7: No polling API (uart_poll_in/out should not be used in async context)
    has_polling = "uart_poll_in" in generated_code or "uart_poll_out" in generated_code
    details.append(
        CheckDetail(
            check_name="no_polling_uart_api",
            passed=not has_polling,
            expected="uart_poll_in/poll_out not used (async API required)",
            actual="polling API found" if has_polling else "clean",
            check_type="constraint",
        )
    )

    return details
