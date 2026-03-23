"""Static analysis checks for Flash Area erase and write."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate flash area code structure."""
    details: list[CheckDetail] = []

    # Check 1: flash_map header included
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

    # Check 2: flash_area_open called
    has_open = "flash_area_open" in generated_code
    details.append(
        CheckDetail(
            check_name="flash_area_open_called",
            passed=has_open,
            expected="flash_area_open() called",
            actual="present" if has_open else "missing",
            check_type="exact_match",
        )
    )

    # Check 3: flash_area_erase called
    has_erase = "flash_area_erase" in generated_code
    details.append(
        CheckDetail(
            check_name="flash_area_erase_called",
            passed=has_erase,
            expected="flash_area_erase() called before write",
            actual="present" if has_erase else "missing",
            check_type="exact_match",
        )
    )

    # Check 4: flash_area_write called
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

    # Check 5: flash_area_close called
    has_close = "flash_area_close" in generated_code
    details.append(
        CheckDetail(
            check_name="flash_area_close_called",
            passed=has_close,
            expected="flash_area_close() called after operations",
            actual="present" if has_close else "missing",
            check_type="exact_match",
        )
    )

    return details
