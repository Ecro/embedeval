"""Behavioral checks for Zephyr USB CDC ACM Kconfig fragment (metamorphic properties)."""

from embedeval.models import CheckDetail

_HALLUCINATED_CONFIGS = [
    "CONFIG_SECURE_MODE",
    "CONFIG_WIFI_BLE_COEX",
    "CONFIG_DEBUG_ENABLE",
    "CONFIG_NETWORK_STACK",
    "CONFIG_AUTO_INIT",
]


def _parse_config(generated_code: str) -> dict[str, str]:
    config: dict[str, str] = {}
    for line in generated_code.strip().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            config[key.strip()] = val.strip()
    return config


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate USB CDC ACM Kconfig dependency chain and config consistency."""
    details: list[CheckDetail] = []
    config = _parse_config(generated_code)

    usb_stack_enabled = config.get("CONFIG_USB_DEVICE_STACK") == "y"
    cdc_acm_enabled = config.get("CONFIG_USB_CDC_ACM") == "y"
    uart_ctrl_enabled = config.get("CONFIG_UART_LINE_CTRL") == "y"

    # Check 1: No hallucinated CONFIG options
    found_hallucinated = [opt for opt in _HALLUCINATED_CONFIGS if opt in generated_code]
    details.append(
        CheckDetail(
            check_name="no_hallucinated_config_options",
            passed=not found_hallucinated,
            expected="No hallucinated Zephyr CONFIG options",
            actual="clean" if not found_hallucinated else f"hallucinated: {found_hallucinated}",
            check_type="hallucination",
        )
    )

    # Check 2: Deprecated option conflict check
    has_newlib = config.get("CONFIG_NEWLIB_LIBC") == "y"
    has_minimal = config.get("CONFIG_MINIMAL_LIBC") == "y"
    no_deprecated_conflict = not (has_newlib and has_minimal)
    details.append(
        CheckDetail(
            check_name="no_newlib_minimal_libc_conflict",
            passed=no_deprecated_conflict,
            expected="CONFIG_NEWLIB_LIBC and CONFIG_MINIMAL_LIBC are mutually exclusive",
            actual=(
                "no conflict"
                if no_deprecated_conflict
                else "both CONFIG_NEWLIB_LIBC=y and CONFIG_MINIMAL_LIBC=y present (conflict)"
            ),
            check_type="constraint",
        )
    )

    # Check 3: Metamorphic: USB_CDC_ACM requires USB_DEVICE_STACK=y
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

    # Check 4: Metamorphic: UART_LINE_CTRL is meaningful only with CDC_ACM
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

    # Check 5: All required configs present AND enabled
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

    # Check 6: No use of CONFIG_USB_SERIAL (wrong/non-existent option)
    # LLM failure: uses CONFIG_USB_SERIAL instead of CONFIG_USB_CDC_ACM
    has_fake_usb_serial = "CONFIG_USB_SERIAL" in generated_code
    details.append(
        CheckDetail(
            check_name="no_fake_usb_serial_option",
            passed=not has_fake_usb_serial,
            expected="CONFIG_USB_SERIAL does not exist; use CONFIG_USB_CDC_ACM",
            actual=(
                "not present"
                if not has_fake_usb_serial
                else "CONFIG_USB_SERIAL used (hallucinated — non-existent Zephyr option)"
            ),
            check_type="hallucination",
        )
    )

    return details
