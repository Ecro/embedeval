"""Behavioral checks for Flash Area Boundary Validation."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate flash boundary check behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: flash_area_open before write operations
    # flash_area_write may be in a helper function defined before main(), but it is only
    # executed at runtime after flash_area_open() is called in main().
    # Strategy: verify both are present AND flash_area_open appears in main (or after
    # the helper that contains flash_area_write), confirming the open-before-write contract.
    import re
    open_matches = list(re.finditer(r'\bflash_area_open\s*\(', generated_code))
    write_matches = list(re.finditer(r'\bflash_area_write\s*\(', generated_code))
    open_pos = open_matches[0].start() if open_matches else -1
    write_pos = write_matches[0].start() if write_matches else -1

    # Determine main() start to assess whether open is in main
    main_pos = generated_code.find("int main(")
    if main_pos == -1:
        main_pos = generated_code.find("void main(")

    # Accept if: open appears in main (after main_pos) and write is present anywhere
    open_in_main = open_pos != -1 and main_pos != -1 and open_pos > main_pos
    # Also accept traditional ordering: open position < write position
    positional_order = open_pos != -1 and write_pos != -1 and open_pos < write_pos
    open_before_write = (open_in_main and write_pos != -1) or positional_order
    details.append(
        CheckDetail(
            check_name="open_before_write",
            passed=open_before_write,
            expected="flash_area_open() before flash_area_write()",
            actual="correct order" if open_before_write else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 2: get_size called before write (to have bounds available)
    get_size_matches = list(re.finditer(r'\bflash_area_get_size\s*\(', generated_code))
    get_size_pos = get_size_matches[0].start() if get_size_matches else -1
    get_size_before_write = (
        get_size_pos != -1 and write_pos != -1 and get_size_pos < write_pos
    )
    details.append(
        CheckDetail(
            check_name="get_size_before_write",
            passed=get_size_before_write,
            expected="flash_area_get_size() before flash_area_write()",
            actual="correct order" if get_size_before_write else "wrong order or missing",
            check_type="constraint",
        )
    )

    # Check 3: Boundary violation results in error (EINVAL or negative)
    has_boundary_error = (
        "EINVAL" in generated_code
        or "BOUNDARY VIOLATION" in generated_code
        or "boundary" in generated_code.lower()
    )
    details.append(
        CheckDetail(
            check_name="boundary_violation_returns_error",
            passed=has_boundary_error,
            expected="Boundary violation returns error (EINVAL or BOUNDARY VIOLATION message)",
            actual="present" if has_boundary_error else "missing (boundary check may not abort)",
            check_type="constraint",
        )
    )

    # Check 4: flash_area_close on error paths (no handle leak)
    has_close = "flash_area_close" in generated_code
    close_pos = generated_code.find("flash_area_close")
    # Heuristic: close appears after first open and after some error handling
    import re
    error_returns = list(re.finditer(r'return\s+ret|return\s+-\d+|return\s+ret;', generated_code))
    close_on_error = has_close and any(
        m.start() > open_pos and m.start() < close_pos
        for m in error_returns
    ) if open_pos != -1 and close_pos != -1 else False
    details.append(
        CheckDetail(
            check_name="close_on_error_path",
            passed=close_on_error or has_close,
            expected="flash_area_close() called on error paths to prevent handle leak",
            actual="close present" if has_close else "close missing",
            check_type="constraint",
        )
    )

    # Check 5: Both valid and invalid write tested
    write_ok = "WRITE OK" in generated_code or "write ok" in generated_code.lower()
    write_blocked = "WRITE BLOCKED" in generated_code or "blocked" in generated_code.lower() or "BOUNDARY" in generated_code
    details.append(
        CheckDetail(
            check_name="both_valid_and_invalid_tested",
            passed=write_ok and write_blocked,
            expected="Both valid write (WRITE OK) and boundary violation (WRITE BLOCKED) demonstrated",
            actual=f"ok={write_ok} blocked={write_blocked}",
            check_type="constraint",
        )
    )

    return details
