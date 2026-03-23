"""Behavioral checks for MCUboot Serial Recovery Mode Kconfig fragment."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate MCUboot serial recovery Kconfig dependency chains and transport exclusion."""
    details: list[CheckDetail] = []
    config: dict[str, str] = {}
    for line in generated_code.strip().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            config[key.strip()] = val.strip()

    mcuboot_serial_enabled = config.get("CONFIG_MCUBOOT_SERIAL") == "y"
    cdc_acm_enabled = config.get("CONFIG_BOOT_SERIAL_CDC_ACM") == "y"
    usb_device_stack_enabled = config.get("CONFIG_USB_DEVICE_STACK") == "y"
    serial_uart_enabled = config.get("CONFIG_BOOT_SERIAL_UART") == "y"

    # Metamorphic: BOOT_SERIAL_CDC_ACM requires MCUBOOT_SERIAL=y
    cdc_acm_needs_serial = not (cdc_acm_enabled and not mcuboot_serial_enabled)
    details.append(
        CheckDetail(
            check_name="boot_serial_cdc_acm_requires_mcuboot_serial",
            passed=cdc_acm_needs_serial,
            expected="BOOT_SERIAL_CDC_ACM requires MCUBOOT_SERIAL=y",
            actual=(
                f"MCUBOOT_SERIAL={config.get('CONFIG_MCUBOOT_SERIAL', 'n')}, "
                f"BOOT_SERIAL_CDC_ACM={config.get('CONFIG_BOOT_SERIAL_CDC_ACM', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Metamorphic: BOOT_SERIAL_CDC_ACM requires USB_DEVICE_STACK=y
    cdc_acm_needs_usb = not (cdc_acm_enabled and not usb_device_stack_enabled)
    details.append(
        CheckDetail(
            check_name="boot_serial_cdc_acm_requires_usb_device_stack",
            passed=cdc_acm_needs_usb,
            expected="BOOT_SERIAL_CDC_ACM requires USB_DEVICE_STACK=y",
            actual=(
                f"USB_DEVICE_STACK={config.get('CONFIG_USB_DEVICE_STACK', 'n')}, "
                f"BOOT_SERIAL_CDC_ACM={config.get('CONFIG_BOOT_SERIAL_CDC_ACM', 'n')}"
            ),
            check_type="constraint",
        )
    )

    # Mutual exclusion: BOOT_SERIAL_CDC_ACM and BOOT_SERIAL_UART are transport alternatives
    no_transport_conflict = not (cdc_acm_enabled and serial_uart_enabled)
    details.append(
        CheckDetail(
            check_name="serial_transport_mutual_exclusion",
            passed=no_transport_conflict,
            expected="BOOT_SERIAL_CDC_ACM and BOOT_SERIAL_UART are mutually exclusive transports",
            actual=(
                "no conflict"
                if no_transport_conflict
                else "both BOOT_SERIAL_CDC_ACM and BOOT_SERIAL_UART set (conflict)"
            ),
            check_type="constraint",
        )
    )

    # Summary: all required configs present
    required = [
        "CONFIG_MCUBOOT_SERIAL",
        "CONFIG_BOOT_SERIAL_CDC_ACM",
        "CONFIG_USB_DEVICE_STACK",
    ]
    all_present = all(config.get(k) == "y" for k in required)
    details.append(
        CheckDetail(
            check_name="all_required_configs_enabled",
            passed=all_present,
            expected="MCUBOOT_SERIAL, BOOT_SERIAL_CDC_ACM, USB_DEVICE_STACK all =y",
            actual=str({k: config.get(k, "missing") for k in required}),
            check_type="exact_match",
        )
    )

    return details
