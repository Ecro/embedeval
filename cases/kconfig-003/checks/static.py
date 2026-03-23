"""Static analysis checks for Zephyr USB CDC ACM Kconfig fragment."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate USB CDC ACM Kconfig fragment format and required options."""
    details: list[CheckDetail] = []
    lines = [
        line.strip()
        for line in generated_code.strip().splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    # Check 1: All lines use CONFIG_ prefix and contain =
    valid_format = all(
        line.startswith("CONFIG_") and "=" in line for line in lines
    )
    details.append(
        CheckDetail(
            check_name="kconfig_format",
            passed=valid_format,
            expected="All lines start with CONFIG_ and contain =",
            actual=f"{len(lines)} lines, format valid: {valid_format}",
            check_type="exact_match",
        )
    )

    # Check 2: CONFIG_USB_DEVICE_STACK=y present
    has_usb_stack = any("CONFIG_USB_DEVICE_STACK=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="usb_device_stack_enabled",
            passed=has_usb_stack,
            expected="CONFIG_USB_DEVICE_STACK=y",
            actual="present" if has_usb_stack else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: CONFIG_USB_CDC_ACM=y present
    has_cdc_acm = any("CONFIG_USB_CDC_ACM=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="usb_cdc_acm_enabled",
            passed=has_cdc_acm,
            expected="CONFIG_USB_CDC_ACM=y",
            actual="present" if has_cdc_acm else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: CONFIG_UART_LINE_CTRL=y present
    has_uart_ctrl = any("CONFIG_UART_LINE_CTRL=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="uart_line_ctrl_enabled",
            passed=has_uart_ctrl,
            expected="CONFIG_UART_LINE_CTRL=y",
            actual="present" if has_uart_ctrl else "missing",
            check_type="exact_match",
        )
    )

    return details
