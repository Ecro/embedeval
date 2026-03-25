"""Behavioral checks for STM32 HAL UART interrupt receive application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate STM32 HAL UART behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: Baud rate configured as 115200
    has_baud = "115200" in generated_code
    details.append(
        CheckDetail(
            check_name="baud_rate_115200_configured",
            passed=has_baud,
            expected="BaudRate = 115200",
            actual="present" if has_baud else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: Interrupt receive (not polling) is the primary receive mechanism
    # LLM failure: uses HAL_UART_Receive (blocking/polling) instead of _IT
    has_receive_it = "HAL_UART_Receive_IT" in generated_code
    has_polling_only = "HAL_UART_Receive" in generated_code and not has_receive_it
    details.append(
        CheckDetail(
            check_name="non_polling_receive",
            passed=has_receive_it and not has_polling_only,
            expected="HAL_UART_Receive_IT used (interrupt mode, not polling)",
            actual="interrupt" if has_receive_it else "polling or missing",
            check_type="constraint",
        )
    )

    # Check 3: RxCpltCallback defined to handle completed receive
    has_rx_callback = "HAL_UART_RxCpltCallback" in generated_code
    details.append(
        CheckDetail(
            check_name="rx_complete_callback_defined",
            passed=has_rx_callback,
            expected="HAL_UART_RxCpltCallback override defined",
            actual="present" if has_rx_callback else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: Receive re-armed in callback (critical: _IT is one-shot, must re-arm)
    # LLM failure: calls Receive_IT once in main but never re-arms in callback
    callback_start = generated_code.find("HAL_UART_RxCpltCallback")
    rearm_in_callback = False
    if callback_start != -1:
        # Look for Receive_IT after the callback definition
        callback_body = generated_code[callback_start:callback_start + 400]
        rearm_in_callback = "HAL_UART_Receive_IT" in callback_body
    details.append(
        CheckDetail(
            check_name="receive_it_rearmed_in_callback",
            passed=rearm_in_callback,
            expected="HAL_UART_Receive_IT re-armed inside RxCpltCallback",
            actual="present" if rearm_in_callback else "missing — one-shot not re-armed",
            check_type="constraint",
        )
    )

    # Check 5: Error callback defined
    has_error_callback = "HAL_UART_ErrorCallback" in generated_code
    details.append(
        CheckDetail(
            check_name="error_callback_defined",
            passed=has_error_callback,
            expected="HAL_UART_ErrorCallback override defined",
            actual="present" if has_error_callback else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: Clock enable before HAL_UART_Init (ordering)
    clk_pos = -1
    for token in ["__HAL_RCC_USART2_CLK_ENABLE", "__HAL_RCC_UART"]:
        pos = generated_code.find(token)
        if pos != -1:
            clk_pos = pos if clk_pos == -1 else min(clk_pos, pos)
    uart_init_pos = generated_code.find("HAL_UART_Init")
    clock_before_init = clk_pos != -1 and uart_init_pos != -1 and clk_pos < uart_init_pos
    details.append(
        CheckDetail(
            check_name="uart_clock_before_init",
            passed=clock_before_init,
            expected="UART clock enabled before HAL_UART_Init",
            actual="correct order" if clock_before_init else "wrong order or missing",
            check_type="constraint",
        )
    )

    return details
