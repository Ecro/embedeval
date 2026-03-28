"""Behavioral checks for flash-efficient CRC-16 implementation."""

import re

from embedeval.check_utils import check_no_cross_platform_apis, strip_comments
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []
    stripped = strip_comments(generated_code)

    # Check 1: Bitwise CRC computation (not table-driven)
    has_bitwise = bool(re.search(r'<<\s*1|>>\s*1|<<\s*8|>>\s*8', stripped))
    has_xor = "^" in stripped and ("0x1021" in stripped or "0x8408" in stripped)
    details.append(CheckDetail(
        check_name="bitwise_crc_computation",
        passed=has_bitwise and has_xor,
        expected="Bitwise shift + XOR with polynomial (not table-driven)",
        actual="bitwise CRC found" if (has_bitwise and has_xor) else "no bitwise CRC pattern",
        check_type="constraint",
    ))

    # Check 2: No float/double (flash waste on M0)
    fp_patterns = [r'\bfloat\b', r'\bdouble\b']
    has_fp = any(re.search(p, stripped) for p in fp_patterns)
    details.append(CheckDetail(
        check_name="no_floating_point",
        passed=not has_fp,
        expected="No floating point (Cortex-M0 has no FPU, software FP bloats flash)",
        actual="clean" if not has_fp else "floating point detected",
        check_type="constraint",
    ))

    # Check 3: No large string literals (flash waste)
    large_strings = re.findall(r'"([^"]{50,})"', stripped)
    details.append(CheckDetail(
        check_name="no_large_string_literals",
        passed=len(large_strings) == 0,
        expected="No large string literals (>50 chars) — wastes flash",
        actual="clean" if not large_strings else f"{len(large_strings)} large strings found",
        check_type="constraint",
    ))

    # Check 4: Test buffer present with data
    has_test_buf = bool(re.search(
        r'(?:uint8_t|unsigned\s+char)\s+\w+\s*\[', stripped
    ))
    details.append(CheckDetail(
        check_name="test_buffer_present",
        passed=has_test_buf,
        expected="Test data buffer defined",
        actual="present" if has_test_buf else "no test buffer found",
        check_type="exact_match",
    ))

    # Check 5: CRC result printed via printk
    has_print = bool(re.search(r'printk\s*\([^)]*[Cc][Rr][Cc]', stripped)) or \
                bool(re.search(r'printk\s*\([^)]*0x%', stripped))
    details.append(CheckDetail(
        check_name="crc_result_printed",
        passed=has_print,
        expected="CRC result printed via printk",
        actual="printed" if has_print else "CRC result not printed",
        check_type="constraint",
    ))

    # Check 6: Initial value 0xFFFF (CCITT standard)
    has_init = "0xFFFF" in generated_code or "0xffff" in generated_code
    details.append(CheckDetail(
        check_name="initial_value_correct",
        passed=has_init,
        expected="CRC initial value 0xFFFF (CCITT standard)",
        actual="present" if has_init else "missing — wrong initial value",
        check_type="exact_match",
    ))

    # Check 7: No cross-platform API contamination
    cross_plat = check_no_cross_platform_apis(generated_code, skip_platforms=["Linux_Userspace"])
    details.append(CheckDetail(
        check_name="no_cross_platform_apis",
        passed=len(cross_plat) == 0,
        expected="No FreeRTOS/Arduino/STM32_HAL APIs",
        actual="clean" if not cross_plat else f"found: {[a for a, _ in cross_plat]}",
        check_type="constraint",
    ))

    return details
