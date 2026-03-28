"""Static analysis checks for flash-efficient CRC-16 implementation."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []

    # Check 1: kernel.h included
    has_header = "zephyr/kernel.h" in generated_code
    details.append(CheckDetail(
        check_name="kernel_header",
        passed=has_header,
        expected="zephyr/kernel.h included",
        actual="present" if has_header else "missing",
        check_type="exact_match",
    ))

    # Check 2: No lookup table (flash-size awareness)
    # LLM failure: generating 256-entry or 16-entry CRC tables as uint16_t arrays.
    # Matches uint16_t array initialisers with 8 or more 3-to-4 digit hex entries.
    # uint8_t test data buffers (single-byte values) are intentionally excluded.
    has_table = bool(re.search(
        r'uint16_t\s+\w+\s*\[\d*\]\s*=\s*\{[^}]*(?:0x[0-9a-fA-F]{3,4}\s*,\s*){7,}',
        generated_code,
    ))
    details.append(CheckDetail(
        check_name="no_lookup_table",
        passed=not has_table,
        expected="No CRC lookup table (flash-size constraint)",
        actual="no table found" if not has_table else "lookup table detected — wastes flash on 16KB target",
        check_type="constraint",
    ))

    # Check 3: No stdio.h (use printk, not printf)
    has_stdio = "stdio.h" in generated_code or "stdlib.h" in generated_code
    details.append(CheckDetail(
        check_name="no_stdio",
        passed=not has_stdio,
        expected="No stdio.h/stdlib.h (use printk for minimal flash)",
        actual="clean" if not has_stdio else "stdio/stdlib included — bloats flash",
        check_type="constraint",
    ))

    # Check 4: CRC polynomial present
    has_poly = "0x1021" in generated_code or "0x8408" in generated_code
    details.append(CheckDetail(
        check_name="crc_polynomial_present",
        passed=has_poly,
        expected="CRC-16-CCITT polynomial 0x1021 or reflected 0x8408",
        actual="present" if has_poly else "missing — wrong or no polynomial",
        check_type="exact_match",
    ))

    # Check 5: Has main function
    has_main = "int main(" in generated_code or "void main(" in generated_code
    details.append(CheckDetail(
        check_name="main_function",
        passed=has_main,
        expected="main() function defined",
        actual="present" if has_main else "missing",
        check_type="exact_match",
    ))

    return details
