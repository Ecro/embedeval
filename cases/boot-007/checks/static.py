"""Static analysis checks for MCUboot Serial Recovery Mode Kconfig fragment."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate MCUboot serial recovery Kconfig fragment format and required options."""
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
            expected="All lines: CONFIG_*=value",
            actual=f"{len(lines)} lines, valid={valid_format}",
            check_type="exact_match",
        )
    )

    # Check 2: CONFIG_MCUBOOT_SERIAL=y present
    has_mcuboot_serial = any("CONFIG_MCUBOOT_SERIAL=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="mcuboot_serial_enabled",
            passed=has_mcuboot_serial,
            expected="CONFIG_MCUBOOT_SERIAL=y",
            actual="present" if has_mcuboot_serial else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: CONFIG_BOOT_SERIAL_CDC_ACM=y present
    has_cdc_acm = any("CONFIG_BOOT_SERIAL_CDC_ACM=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="boot_serial_cdc_acm_enabled",
            passed=has_cdc_acm,
            expected="CONFIG_BOOT_SERIAL_CDC_ACM=y",
            actual="present" if has_cdc_acm else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: CONFIG_USB_DEVICE_STACK=y required by CDC_ACM
    has_usb = any("CONFIG_USB_DEVICE_STACK=y" in line for line in lines)
    details.append(
        CheckDetail(
            check_name="usb_device_stack_enabled",
            passed=has_usb,
            expected="CONFIG_USB_DEVICE_STACK=y",
            actual="present" if has_usb else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: BOOT_SERIAL_UART must NOT coexist with BOOT_SERIAL_CDC_ACM
    has_serial_uart = any("CONFIG_BOOT_SERIAL_UART=y" in line for line in lines)
    no_transport_conflict = not (has_cdc_acm and has_serial_uart)
    details.append(
        CheckDetail(
            check_name="no_serial_transport_conflict",
            passed=no_transport_conflict,
            expected="BOOT_SERIAL_CDC_ACM and BOOT_SERIAL_UART are mutually exclusive",
            actual="no conflict" if no_transport_conflict else "both CDC_ACM and UART serial transports set",
            check_type="constraint",
        )
    )

    return details
