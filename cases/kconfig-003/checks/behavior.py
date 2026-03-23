"""Behavioral checks for Zephyr USB CDC ACM Kconfig fragment (metamorphic properties)."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate USB CDC ACM Kconfig dependency chain and config consistency."""
    details: list[CheckDetail] = []
    lines = [
        line.strip()
        for line in generated_code.strip().splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    config: dict[str, str] = {}
    for line in lines:
        if "=" in line:
            key, val = line.split("=", 1)
            config[key.strip()] = val.strip()

    usb_stack_enabled = config.get("CONFIG_USB_DEVICE_STACK") == "y"
    cdc_acm_enabled = config.get("CONFIG_USB_CDC_ACM") == "y"
    uart_ctrl_enabled = config.get("CONFIG_UART_LINE_CTRL") == "y"

    # Metamorphic: USB_CDC_ACM requires USB_DEVICE_STACK=y
    cdc_requires_usb_stack = not (cdc_acm_enabled and not usb_stack_enabled)
    details.append(
        CheckDetail(
            check_name="cdc_acm_requires_usb_device_stack",
            passed=cdc_requires_usb_stack,
            expected="USB_CDC_ACM requires USB_DEVICE_STACK=y",
            actual=(
                f"USB_DEVICE_STACK={config.get('CONFIG_USB_DEVICE_STACK', 'n')}, "
                f"USB_CDC_ACM={config.get('CONFIG_USB_CDC_ACM', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Metamorphic: UART_LINE_CTRL is meaningful only with CDC_ACM
    uart_ctrl_consistent = not (uart_ctrl_enabled and not cdc_acm_enabled)
    details.append(
        CheckDetail(
            check_name="uart_line_ctrl_requires_cdc_acm",
            passed=uart_ctrl_consistent,
            expected="UART_LINE_CTRL is only useful when USB_CDC_ACM=y",
            actual=(
                f"USB_CDC_ACM={config.get('CONFIG_USB_CDC_ACM', 'n')}, "
                f"UART_LINE_CTRL={config.get('CONFIG_UART_LINE_CTRL', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Check: all required configs present AND enabled
    required_configs = [
        "CONFIG_USB_DEVICE_STACK",
        "CONFIG_USB_CDC_ACM",
        "CONFIG_UART_LINE_CTRL",
    ]
    all_present = all(config.get(k) == "y" for k in required_configs)
    details.append(
        CheckDetail(
            check_name="all_required_configs_enabled",
            passed=all_present,
            expected="USB_DEVICE_STACK, USB_CDC_ACM, UART_LINE_CTRL all =y",
            actual=str({k: config.get(k, "missing") for k in required_configs}),
            check_type="exact_match",
        )
    )

    return details
