"""Behavioral checks for Yocto machine configuration fragment."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Yocto machine .conf behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: KERNEL_DEVICETREE ends with .dtb (not .dts source file)
    # (LLM failure: specifying .dts source instead of compiled .dtb blob)
    has_dtb = ".dtb" in generated_code
    has_dts_only = ".dts" in generated_code and not has_dtb
    details.append(
        CheckDetail(
            check_name="kernel_devicetree_ends_in_dtb",
            passed=has_dtb,
            expected="KERNEL_DEVICETREE value ends in .dtb (compiled blob, not .dts source)",
            actual="present" if has_dtb else "WRONG: use .dtb not .dts in KERNEL_DEVICETREE",
            check_type="constraint",
        )
    )

    # Check 2: SERIAL_CONSOLES uses "baudrate;device" format with semicolon
    # (LLM failure: "115200:ttyAMA0" with colon, or "115200 ttyAMA0" with space)
    import re
    serial_correct = bool(re.search(r'SERIAL_CONSOLES\s*=\s*"[0-9]+;tty', generated_code))
    details.append(
        CheckDetail(
            check_name="serial_consoles_correct_format",
            passed=serial_correct,
            expected='SERIAL_CONSOLES = "baudrate;device" format with semicolon',
            actual="correct" if serial_correct else "WRONG FORMAT: use baudrate;device with semicolon",
            check_type="constraint",
        )
    )

    # Check 3: MACHINE_FEATURES has at least one valid feature
    machine_features_list = ["usbhost", "ethernet", "ext2", "vfat", "wifi", "bluetooth", "alsa", "screen", "touchscreen"]
    has_valid_feature = any(f in generated_code for f in machine_features_list)
    details.append(
        CheckDetail(
            check_name="machine_features_valid_values",
            passed=has_valid_feature,
            expected=f"MACHINE_FEATURES contains valid features (e.g. {', '.join(machine_features_list[:3])})",
            actual="present" if has_valid_feature else "no recognized features found",
            check_type="constraint",
        )
    )

    # Check 4: No .dts in KERNEL_DEVICETREE (anti-check)
    has_dts_wrong = bool(re.search(r'KERNEL_DEVICETREE\s*=\s*"[^"]*\.dts"', generated_code))
    details.append(
        CheckDetail(
            check_name="no_dts_in_kernel_devicetree",
            passed=not has_dts_wrong,
            expected="No .dts extension in KERNEL_DEVICETREE (use .dtb)",
            actual="clean" if not has_dts_wrong else "WRONG: .dts specified (must be .dtb)",
            check_type="constraint",
        )
    )

    # Check 5: Serial device is a valid Linux TTY name
    has_valid_tty = bool(re.search(r'tty(AMA|S|USB|MXC|SAC)\d', generated_code))
    details.append(
        CheckDetail(
            check_name="serial_device_valid_tty_name",
            passed=has_valid_tty,
            expected="Serial device uses valid Linux TTY name (ttyAMA0, ttyS0, etc.)",
            actual="present" if has_valid_tty else "no recognized TTY device name",
            check_type="constraint",
        )
    )

    return details
