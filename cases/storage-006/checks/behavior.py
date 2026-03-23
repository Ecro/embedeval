"""Behavioral checks for Wear-Aware Flash Write with Sector Rotation."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate wear-aware flash write behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: flash_erase before flash_write (mandatory for flash)
    erase_pos = generated_code.find("flash_erase")
    write_pos = generated_code.find("flash_write")
    erase_before_write = erase_pos != -1 and write_pos != -1 and erase_pos < write_pos
    details.append(
        CheckDetail(
            check_name="erase_before_write",
            passed=erase_before_write,
            expected="flash_erase() appears before flash_write() (erase required before flash write)",
            actual="correct order" if erase_before_write else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: Write count incremented after successful write
    import re
    write_count_inc = bool(
        re.search(r'write_count\[.*\]\s*\+\+', generated_code)
        or re.search(r'write_count\[.*\]\s*\+=\s*1', generated_code)
        or re.search(r'\+\+\s*write_count', generated_code)
    )
    details.append(
        CheckDetail(
            check_name="write_count_incremented",
            passed=write_count_inc,
            expected="Write count incremented after each successful write",
            actual="present" if write_count_inc else "missing (write count not updated)",
            check_type="constraint",
        )
    )

    # Check 3: Return value of flash_erase checked
    erase_ret_checked = bool(
        re.search(r'flash_erase\s*\(.*\)\s*[;<]', generated_code)
        and ("< 0" in generated_code or "!= 0" in generated_code or "ret" in generated_code)
    )
    details.append(
        CheckDetail(
            check_name="flash_erase_return_checked",
            passed=erase_ret_checked,
            expected="Return value of flash_erase() checked",
            actual="checked" if erase_ret_checked else "return value may be ignored",
            check_type="constraint",
        )
    )

    # Check 4: Multiple writes performed (at least 3 calls in main)
    write_calls = len(re.findall(r'\bflash_write\b|\bwear_write\b', generated_code))
    details.append(
        CheckDetail(
            check_name="multiple_writes_performed",
            passed=write_calls >= 3,
            expected="At least 3 write operations performed",
            actual=f"found {write_calls} write call(s)",
            check_type="constraint",
        )
    )

    # Check 5: device_is_ready or similar device check
    has_ready_check = "device_is_ready" in generated_code or "IS_ENABLED" in generated_code
    details.append(
        CheckDetail(
            check_name="device_ready_checked",
            passed=has_ready_check,
            expected="device_is_ready() called to verify flash device",
            actual="present" if has_ready_check else "missing (no device validation)",
            check_type="constraint",
        )
    )

    # Check 6: Success message printed
    has_ok_print = "WEAR WRITE OK" in generated_code or "OK" in generated_code
    details.append(
        CheckDetail(
            check_name="success_printed",
            passed=has_ok_print,
            expected="Success message printed after each write",
            actual="present" if has_ok_print else "missing",
            check_type="constraint",
        )
    )

    return details
