"""Static analysis checks for Flash Area Boundary Validation."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate flash area boundary check code structure."""
    details: list[CheckDetail] = []

    # Check 1: flash_map.h included
    has_flash_map_h = "zephyr/storage/flash_map.h" in generated_code
    details.append(
        CheckDetail(
            check_name="flash_map_header_included",
            passed=has_flash_map_h,
            expected="zephyr/storage/flash_map.h included",
            actual="present" if has_flash_map_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: flash_area_get_size called for boundary reference
    has_get_size = "flash_area_get_size" in generated_code
    details.append(
        CheckDetail(
            check_name="flash_area_get_size_called",
            passed=has_get_size,
            expected="flash_area_get_size() called to get area bounds",
            actual="present" if has_get_size else "missing (no area size reference)",
            check_type="exact_match",
        )
    )

    # Check 3: offset + size <= area_size boundary check present
    # Look for the key comparison pattern
    has_boundary_check = bool(
        re.search(r'offset\s*\+\s*\w*size\w*\s*[><=]', generated_code)
        or re.search(r'\w*size\w*\s*\+\s*offset\s*[><=]', generated_code)
        or re.search(r'offset\s*\+\s*len\w*\s*[><=]', generated_code)
    )
    details.append(
        CheckDetail(
            check_name="offset_plus_size_boundary_check",
            passed=has_boundary_check,
            expected="offset + size compared against area_size (boundary check)",
            actual="present" if has_boundary_check else "missing (no out-of-bounds check!)",
            check_type="constraint",
        )
    )

    # Check 4: size > 0 check
    has_size_check = bool(
        re.search(r'size\s*==\s*0|size\s*<=\s*0|!\s*size', generated_code)
        or re.search(r'len\s*==\s*0', generated_code)
    )
    details.append(
        CheckDetail(
            check_name="zero_size_check",
            passed=has_size_check,
            expected="size > 0 validated before write",
            actual="present" if has_size_check else "missing (zero-size write not guarded)",
            check_type="constraint",
        )
    )

    # Check 5: flash_area_write called
    has_write = "flash_area_write" in generated_code
    details.append(
        CheckDetail(
            check_name="flash_area_write_called",
            passed=has_write,
            expected="flash_area_write() called",
            actual="present" if has_write else "missing",
            check_type="exact_match",
        )
    )

    # Check 6: flash_area_close called (resource cleanup)
    has_close = "flash_area_close" in generated_code
    details.append(
        CheckDetail(
            check_name="flash_area_closed",
            passed=has_close,
            expected="flash_area_close() called to release flash area handle",
            actual="present" if has_close else "missing (flash area handle leaked)",
            check_type="constraint",
        )
    )

    return details
