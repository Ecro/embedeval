"""Behavioral checks for MCUboot Serial Recovery Mode Kconfig fragment."""

from embedeval.models import CheckDetail


def _parse_config(generated_code: str) -> dict[str, str]:
    config: dict[str, str] = {}
    for line in generated_code.strip().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            config[key.strip()] = val.strip()
    return config


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate MCUboot serial recovery Kconfig dependency chains and transport exclusion."""
    details: list[CheckDetail] = []
    config = _parse_config(generated_code)

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

    # Signing type mutual exclusion — RSA vs ECDSA_P256
    # (LLM failure: setting both RSA and ECDSA signature types simultaneously)
    sig_rsa = config.get("CONFIG_BOOT_SIGNATURE_TYPE_RSA") == "y"
    sig_ec256 = config.get("CONFIG_BOOT_SIGNATURE_TYPE_ECDSA_P256") == "y"
    sig_ed25519 = config.get("CONFIG_BOOT_SIGNATURE_TYPE_ED25519") == "y"
    sig_types_set = sum([sig_rsa, sig_ec256, sig_ed25519])
    no_sig_conflict = sig_types_set <= 1
    details.append(
        CheckDetail(
            check_name="signature_type_mutual_exclusion",
            passed=no_sig_conflict,
            expected="Only one signature type (RSA, ECDSA_P256, or ED25519) may be set",
            actual="no conflict" if no_sig_conflict else f"CONFLICT: {sig_types_set} signature types set simultaneously",
            check_type="constraint",
        )
    )

    # UPGRADE_ONLY + SWAP_USING_MOVE conflict
    has_upgrade_only = config.get("CONFIG_BOOT_UPGRADE_ONLY") == "y"
    has_swap_move = config.get("CONFIG_BOOT_SWAP_USING_MOVE") == "y"
    no_swap_conflict = not (has_upgrade_only and has_swap_move)
    details.append(
        CheckDetail(
            check_name="no_upgrade_only_swap_conflict",
            passed=no_swap_conflict,
            expected="BOOT_UPGRADE_ONLY and BOOT_SWAP_USING_MOVE must not both be set",
            actual="no conflict" if no_swap_conflict else "CONFLICT: UPGRADE_ONLY + SWAP_USING_MOVE both set",
            check_type="constraint",
        )
    )

    # SINGLE_APPLICATION_SLOT + SWAP conflict
    has_single = config.get("CONFIG_SINGLE_APPLICATION_SLOT") == "y"
    has_any_swap = (
        config.get("CONFIG_BOOT_SWAP_USING_MOVE") == "y"
        or config.get("CONFIG_BOOT_SWAP_USING_SCRATCH") == "y"
    )
    no_single_swap_conflict = not (has_single and has_any_swap)
    details.append(
        CheckDetail(
            check_name="no_single_slot_swap_conflict",
            passed=no_single_swap_conflict,
            expected="SINGLE_APPLICATION_SLOT and BOOT_SWAP_* cannot both be set",
            actual="no conflict" if no_single_swap_conflict else "CONFLICT: single slot + swap both set",
            check_type="constraint",
        )
    )

    return details
