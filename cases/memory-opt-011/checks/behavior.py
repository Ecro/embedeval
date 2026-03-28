"""Behavioral checks for RAM budget constraint on 32KB target."""

import re

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis

# Map C type names to byte widths for accurate RAM estimation
_TYPE_WIDTHS = {
    "uint8_t": 1, "int8_t": 1, "char": 1,
    "uint16_t": 2, "int16_t": 2,
    "uint32_t": 4, "int32_t": 4, "float": 4, "int": 4,
    "double": 8,
}

_TYPE_PATTERN = (
    r"(uint8_t|uint16_t|uint32_t|int8_t|int16_t|int32_t"
    r"|char|int|float|double)"
)


def _resolve_size_expr(expr: str, define_vals: dict[str, int]) -> int:
    """Resolve a size expression like '16', 'BUF_SIZE', or 'A * B'."""
    expr = expr.strip()
    # Pure integer
    try:
        return int(expr)
    except ValueError:
        pass
    # Single define
    if expr in define_vals:
        return define_vals[expr]
    # Product of two defines: A * B
    parts = re.split(r"\s*\*\s*", expr)
    if len(parts) == 2:
        a = define_vals.get(parts[0].strip(), 0)
        b = define_vals.get(parts[1].strip(), 0)
        if a and b:
            return a * b
    return 0


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate RAM-constrained buffer sizing."""
    details: list[CheckDetail] = []

    # Collect #define values
    define_vals: dict[str, int] = {}
    for m in re.finditer(r"#define\s+(\w+)\s+(\d+)", generated_code):
        define_vals[m.group(1)] = int(m.group(2))

    # Find all static array declarations with byte-accurate sizes
    array_bytes: list[int] = []
    for m in re.finditer(
        _TYPE_PATTERN + r"\s+\w+\s*\[\s*([^]]+)\s*\]",
        generated_code,
    ):
        type_name = m.group(1)
        size_expr = m.group(2)
        elem_bytes = _TYPE_WIDTHS.get(type_name, 1)
        elem_count = _resolve_size_expr(size_expr, define_vals)
        if elem_count > 0:
            array_bytes.append(elem_count * elem_bytes)

    # Check 1: No single buffer exceeds 4KB
    max_buf = max(array_bytes) if array_bytes else 0
    details.append(
        CheckDetail(
            check_name="no_oversized_buffer",
            passed=max_buf <= 4096,
            expected="No single buffer > 4096 bytes "
            "(4KB limit for 32KB RAM target)",
            actual=f"largest buffer: {max_buf} bytes"
            if array_bytes else "no static arrays found",
            check_type="constraint",
        )
    )

    # Check 2: Total static allocation reasonable (< 8KB)
    total = sum(array_bytes)
    details.append(
        CheckDetail(
            check_name="total_static_allocation_bounded",
            passed=total <= 8192,
            expected="Total static buffer allocation < 8KB",
            actual=f"total: {total} bytes",
            check_type="constraint",
        )
    )

    # Check 3: Uses #define for buffer sizes, not magic numbers
    raw_numeric = len(re.findall(
        _TYPE_PATTERN + r"\s+\w+\s*\[\s*\d{3,}\s*\]",
        generated_code,
    ))
    details.append(
        CheckDetail(
            check_name="no_magic_buffer_sizes",
            passed=raw_numeric == 0,
            expected="Buffer sizes use #define constants, not magic numbers",
            actual="clean" if raw_numeric == 0
            else f"{raw_numeric} buffers with hardcoded numeric sizes (>99)",
            check_type="constraint",
        )
    )

    # Check 4: Uses printk (not printf — embedded target)
    has_printk = "printk(" in generated_code
    has_only_printf = "printf(" in generated_code and "printk(" not in generated_code
    details.append(
        CheckDetail(
            check_name="uses_printk_not_printf",
            passed=has_printk and not has_only_printf,
            expected="Uses printk (Zephyr), not printf (POSIX)",
            actual="printk used" if has_printk else "printf used or no output",
            check_type="constraint",
        )
    )

    # Check: No cross-platform API contamination
    cross_plat = check_no_cross_platform_apis(generated_code, skip_platforms=["Linux_Userspace"])
    details.append(CheckDetail(
        check_name="no_cross_platform_apis",
        passed=len(cross_plat) == 0,
        expected="No FreeRTOS/Arduino/STM32_HAL/POSIX APIs",
        actual="clean" if not cross_plat else f"found: {[a for a, _ in cross_plat]}",
        check_type="constraint",
    ))

    return details
