"""Behavioral checks for Yocto machine configuration fragment."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate Yocto machine .conf behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: KERNEL_DEVICETREE ends with .dtb (not .dts source file)
    # (LLM failure: specifying .dts source instead of compiled .dtb blob)
    has_dtb = ".dtb" in generated_code
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

    # Check 6: SPDX license format if LICENSE present
    non_spdx_patterns = [
        r'\bGPLv2\b', r'\bGPLv3\b', r'\bLGPLv2\b',
        r'\bLGPLv3\b', r'"GPL-2\.0"[^-]', r'"GPL-3\.0"[^-]',
    ]
    has_non_spdx = any(re.search(p, generated_code) for p in non_spdx_patterns)
    details.append(
        CheckDetail(
            check_name="spdx_license_format",
            passed=not has_non_spdx,
            expected="SPDX license identifier if set (GPL-2.0-only, not GPLv2)",
            actual="correct SPDX" if not has_non_spdx else "NON-SPDX license name found",
            check_type="constraint",
        )
    )

    # Check 7: Override syntax uses ':' not '_' (Yocto 4.0+ requirement)
    # Machine conf files sometimes set RDEPENDS or similar
    deprecated_override = re.search(
        r'\b(RDEPENDS|FILES|PACKAGES|MACHINE_FEATURES)_\$\{(?:PN|MACHINE)\}',
        generated_code,
    )
    details.append(
        CheckDetail(
            check_name="colon_override_syntax",
            passed=deprecated_override is None,
            expected="Override syntax uses ':' (Yocto 4.0+ requirement)",
            actual="correct" if deprecated_override is None else f"DEPRECATED '_' override: {deprecated_override.group(0)}",
            check_type="constraint",
        )
    )

    # Check 8: No hardcoded absolute paths (machine conf should use variables)
    has_hardcoded = bool(re.search(r'(?<!\$\{D\})/usr/(bin|lib|sbin)\b', generated_code))
    details.append(
        CheckDetail(
            check_name="no_hardcoded_paths",
            passed=not has_hardcoded,
            expected="No hardcoded /usr/* paths in machine conf",
            actual="correct" if not has_hardcoded else "hardcoded paths found in machine conf",
            check_type="constraint",
        )
    )

    # Check 9: KERNEL_IMAGETYPE set to a recognized type (not custom string)
    kernel_image_types = ["zImage", "uImage", "Image", "bzImage", "vmlinux"]
    has_kernel_type = any(t in generated_code for t in kernel_image_types)
    # Only check if KERNEL_IMAGETYPE is set at all
    has_kernel_imagetype = "KERNEL_IMAGETYPE" in generated_code
    kernel_type_ok = (not has_kernel_imagetype) or has_kernel_type
    details.append(
        CheckDetail(
            check_name="kernel_imagetype_recognized",
            passed=kernel_type_ok,
            expected=f"KERNEL_IMAGETYPE is a recognized type: {', '.join(kernel_image_types)}",
            actual="correct" if kernel_type_ok else "unrecognized KERNEL_IMAGETYPE value",
            check_type="constraint",
        )
    )

    # Check 10: No 'require' used to include class files (should use 'inherit')
    has_require_class = bool(re.search(r'^require\s+\S+\.bbclass\b', generated_code, re.MULTILINE))
    details.append(
        CheckDetail(
            check_name="no_require_for_bbclass",
            passed=not has_require_class,
            expected="'inherit' used for .bbclass files, not 'require'",
            actual="correct" if not has_require_class else "WRONG: 'require' used for .bbclass (use 'inherit')",
            check_type="constraint",
        )
    )

    return details
