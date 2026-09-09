"""Behavioral checks for image version check before OTA update."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis
from embedeval.check_utils import scoped_contains
from embedeval.check_utils import find_in_code


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate image version comparison behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: Reads bank header before comparing versions
    # (LLM failure: hardcoding version, not reading from flash)
    header_pos = find_in_code(generated_code, "boot_read_bank_header")
    details.append(
        CheckDetail(
            check_name="reads_bank_header",
            passed=header_pos != -1,
            expected="boot_read_bank_header() called to get running version",
            actual="present" if header_pos != -1 else "missing (hardcoded version?)",
            check_type="constraint",
        )
    )

    # Check 2: Version comparison performed (not unconditionally accepting)
    # (LLM failure: always proceeding without comparing versions)
    has_comparison = any(
        op in generated_code
        for op in ["major", "minor", "revision"]
    ) and (
        scoped_contains(generated_code, '>', scope='code_only') or scoped_contains(generated_code, '<', scope='code_only') or scoped_contains(generated_code, '!=', scope='code_only')
    )
    details.append(
        CheckDetail(
            check_name="version_comparison",
            passed=has_comparison,
            expected="Version fields compared (major, minor, revision)",
            actual="present" if has_comparison else "missing (always accepting update?)",
            check_type="constraint",
        )
    )

    # Check 3: Rejection path exists (not always proceeding with OTA)
    has_rejection = "reject" in generated_code.lower() or (
        "not newer" in generated_code.lower()
    ) or (
        scoped_contains(generated_code, 'return 0', scope='code_only') and "version" in generated_code.lower()
    )
    details.append(
        CheckDetail(
            check_name="rejection_path",
            passed=has_rejection,
            expected="Explicit rejection path when offered version is not newer",
            actual="present" if has_rejection else "missing (always accepting)",
            check_type="constraint",
        )
    )

    # Check 4: Error check on boot_read_bank_header return value
    has_header_err = scoped_contains(generated_code, 'boot_read_bank_header', scope='code_only') and (
        scoped_contains(generated_code, '< 0', scope='code_only') or scoped_contains(generated_code, '!= 0', scope='code_only')
    )
    details.append(
        CheckDetail(
            check_name="header_read_error_handling",
            passed=has_header_err,
            expected="Return value of boot_read_bank_header() checked",
            actual="present" if has_header_err else "missing",
            check_type="constraint",
        )
    )

    # Check 5: Running version printed at startup
    has_running_print = (
        scoped_contains(generated_code, 'Running version', scope='code_only') or "running version" in generated_code.lower()
    )
    details.append(
        CheckDetail(
            check_name="running_version_printed",
            passed=has_running_print,
            expected="Running version printed at startup",
            actual="present" if has_running_print else "missing",
            check_type="constraint",
        )
    )

    # Check 6: Version comparison function checks all three fields (major, minor, revision)
    # (LLM failure: only comparing major version — misses minor/patch differences)
    checks_all_fields = (
        scoped_contains(generated_code, 'major', scope='code_only')
        and scoped_contains(generated_code, 'minor', scope='code_only')
        and scoped_contains(generated_code, 'revision', scope='code_only')
    )
    details.append(
        CheckDetail(
            check_name="all_version_fields_compared",
            passed=checks_all_fields,
            expected="Version comparison covers major, minor, AND revision fields",
            actual="all fields checked" if checks_all_fields else "missing: not all version fields compared (incomplete version check)",
            check_type="constraint",
        )
    )

    # Check 7: boot_read_bank_header return value checked before accessing struct fields
    # (LLM failure: accessing header struct fields even when read fails)
    header_err_pos = -1
    if scoped_contains(generated_code, 'boot_read_bank_header', scope='code_only'):
        header_call_pos = find_in_code(generated_code, "boot_read_bank_header")
        # Look for error check near the header call (within 300 chars)
        nearby = generated_code[header_call_pos:header_call_pos + 300]
        if "< 0" in nearby or "!= 0" in nearby or "ret" in nearby:
            header_err_pos = header_call_pos
    header_checked_before_use = header_err_pos != -1
    details.append(
        CheckDetail(
            check_name="header_return_checked_before_struct_access",
            passed=header_checked_before_use,
            expected="boot_read_bank_header() return value checked before accessing header struct",
            actual="present" if header_checked_before_use else "missing (accessing struct on failed read!)",
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
