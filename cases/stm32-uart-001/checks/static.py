"""Static analysis checks for STM32 HAL UART interrupt receive application."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate STM32 HAL UART code structure and required elements."""
    details: list[CheckDetail] = []

    # Check 1: STM32 HAL header (not Zephyr/Arduino)
    has_hal_header = "stm32f4xx_hal.h" in generated_code
    details.append(
        CheckDetail(
            check_name="stm32_hal_header_included",
            passed=has_hal_header,
            expected="stm32f4xx_hal.h included",
            actual="present" if has_hal_header else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: UART_HandleTypeDef used
    has_uart_handle = "UART_HandleTypeDef" in generated_code
    details.append(
        CheckDetail(
            check_name="uart_handle_typedef_used",
            passed=has_uart_handle,
            expected="UART_HandleTypeDef struct used",
            actual="present" if has_uart_handle else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: Interrupt receive used (not polling HAL_UART_Receive)
    has_receive_it = "HAL_UART_Receive_IT" in generated_code
    details.append(
        CheckDetail(
            check_name="interrupt_receive_used",
            passed=has_receive_it,
            expected="HAL_UART_Receive_IT() used (not polling)",
            actual="present" if has_receive_it else "missing or polling only",
            check_type="exact_match",
        )
    )

    # Check 4: No cross-platform hallucinations
    has_zephyr = any(
        p in generated_code
        for p in ["k_sleep", "uart_rx_enable", "printk(", "zephyr/", "DEVICE_DT_GET"]
    )
    has_espidf = any(p in generated_code for p in ["esp_", "uart_driver_install"])
    has_arduino = any(p in generated_code for p in ["Serial.", "HardwareSerial"])
    no_hallucination = not has_zephyr and not has_espidf and not has_arduino
    details.append(
        CheckDetail(
            check_name="no_cross_platform_hallucination",
            passed=no_hallucination,
            expected="Only STM32 HAL UART APIs used",
            actual="clean" if no_hallucination else f"zephyr={has_zephyr} espidf={has_espidf} arduino={has_arduino}",
            check_type="constraint",
        )
    )

    # Check 5: USART2 instance configured
    has_usart2 = "USART2" in generated_code
    details.append(
        CheckDetail(
            check_name="usart2_instance_configured",
            passed=has_usart2,
            expected="USART2 instance used",
            actual="present" if has_usart2 else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: UART clock enable
    has_uart_clk = any(
        p in generated_code
        for p in ["__HAL_RCC_USART2_CLK_ENABLE", "__HAL_RCC_UART", "RCC_APB1ENR"]
    )
    details.append(
        CheckDetail(
            check_name="uart_clock_enabled",
            passed=has_uart_clk,
            expected="USART2 peripheral clock enabled",
            actual="present" if has_uart_clk else "missing",
            check_type="exact_match",
        )
    )

    return details
