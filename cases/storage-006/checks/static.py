"""Static analysis checks for Wear-Aware Flash Write with Sector Rotation."""

import re

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate wear-aware flash write code structure."""
    details: list[CheckDetail] = []

    # Check 1: flash.h included
    has_flash_h = "zephyr/drivers/flash.h" in generated_code
    details.append(
        CheckDetail(
            check_name="flash_header_included",
            passed=has_flash_h,
            expected="zephyr/drivers/flash.h included",
            actual="present" if has_flash_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: Write count tracked (array or variable for per-sector counting)
    has_write_count = bool(
        re.search(r'write_count', generated_code)
        or re.search(r'write_cnt', generated_code)
        or re.search(r'sector_count', generated_code)
        or re.search(r'erase_count', generated_code)
    )
    details.append(
        CheckDetail(
            check_name="write_count_tracked",
            passed=has_write_count,
            expected="Per-sector write count tracked (write_count[] or similar)",
            actual="present" if has_write_count else "missing (no write tracking)",
            check_type="constraint",
        )
    )

    # Check 3: Rotation/threshold logic present
    has_threshold = bool(
        re.search(r'WRITE_THRESHOLD|ERASE_THRESHOLD|MAX_WRITES|threshold', generated_code)
        or re.search(r'>= *\d+|> *\d+', generated_code)
    )
    details.append(
        CheckDetail(
            check_name="rotation_threshold_defined",
            passed=has_threshold,
            expected="Write threshold defined for triggering sector rotation",
            actual="present" if has_threshold else "missing (no threshold/rotation logic)",
            check_type="constraint",
        )
    )

    # Check 4: Modulo used for sector wrap-around
    has_modulo = "%" in generated_code and "NUM_SECTORS" in generated_code or (
        bool(re.search(r'\w+\s*%\s*\w*[Ss]ector', generated_code))
        or bool(re.search(r'\w*[Ss]ector\w*\s*%\s*\w+', generated_code))
        or bool(re.search(r'current_sector\s*=.*%', generated_code))
    )
    details.append(
        CheckDetail(
            check_name="sector_rotation_with_modulo",
            passed=has_modulo,
            expected="Sector rotation uses modulo (%) for wrap-around",
            actual="present" if has_modulo else "missing or incorrect rotation logic",
            check_type="constraint",
        )
    )

    # Check 5: flash_erase called before write on new sector
    has_erase = "flash_erase" in generated_code
    details.append(
        CheckDetail(
            check_name="flash_erase_called",
            passed=has_erase,
            expected="flash_erase() called to erase sector before writing",
            actual="present" if has_erase else "missing (flash must be erased before write)",
            check_type="exact_match",
        )
    )

    # Check 6: flash_write called
    has_write = "flash_write" in generated_code
    details.append(
        CheckDetail(
            check_name="flash_write_called",
            passed=has_write,
            expected="flash_write() called",
            actual="present" if has_write else "missing",
            check_type="exact_match",
        )
    )

    return details
