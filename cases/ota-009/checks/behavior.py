"""Behavioral checks for OTA image slot status query."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate OTA slot status query behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: Both slots checked (not just primary)
    # (LLM failure: only reading slot 0, never checking secondary slot)
    has_slot0 = "slot0_partition" in generated_code or "FIXED_PARTITION_ID" in generated_code
    has_slot1 = "slot1_partition" in generated_code
    details.append(
        CheckDetail(
            check_name="both_slots_checked",
            passed=has_slot0 and has_slot1,
            expected="Both primary (slot0) and secondary (slot1) slots checked",
            actual="both checked" if (has_slot0 and has_slot1)
                   else f"missing: {'slot0' if not has_slot0 else 'slot1'}",
            check_type="constraint",
        )
    )

    # Check 2: Empty secondary slot handled (non-zero return from boot_read_bank_header)
    # (LLM failure: assuming secondary is always populated, crashing on empty)
    bank_header_pos = generated_code.find("boot_read_bank_header")
    has_error_handling = (
        bank_header_pos != -1
        and ("!= 0" in generated_code or "< 0" in generated_code
             or "empty" in generated_code.lower() or "unreadable" in generated_code.lower())
    )
    details.append(
        CheckDetail(
            check_name="empty_slot_handled",
            passed=has_error_handling,
            expected="boot_read_bank_header() return value checked; empty slot handled gracefully",
            actual="handled" if has_error_handling
                   else "missing — no error check on boot_read_bank_header (crashes on empty slot!)",
            check_type="constraint",
        )
    )

    # Check 3: Version info extracted from header (not hardcoded)
    # (LLM failure: printing "version: 1.0.0" without reading from header struct)
    has_version_from_header = (
        "sem_ver" in generated_code
        or "h.v1" in generated_code
        or "major" in generated_code.lower()
        or "header.h" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="version_from_header_struct",
            passed=has_version_from_header,
            expected="Version info extracted from mcuboot_img_header struct (not hardcoded)",
            actual="from header" if has_version_from_header
                   else "missing or hardcoded version",
            check_type="constraint",
        )
    )

    # Check 4: Swap type printed as human-readable string
    # (LLM failure: printing raw integer with no meaning)
    has_swap_strings = (
        "BOOT_SWAP_TYPE_NONE" in generated_code
        or "BOOT_SWAP_TYPE_TEST" in generated_code
        or "No swap" in generated_code
        or "Test swap" in generated_code
        or "swap_type" in generated_code.lower()
    )
    details.append(
        CheckDetail(
            check_name="swap_type_human_readable",
            passed=has_swap_strings,
            expected="Swap type displayed as human-readable string (not raw integer)",
            actual="human-readable" if has_swap_strings else "missing (raw integer only)",
            check_type="constraint",
        )
    )

    # Check 5: boot_is_img_confirmed reported
    has_confirmed_report = "boot_is_img_confirmed" in generated_code
    details.append(
        CheckDetail(
            check_name="confirmed_status_reported",
            passed=has_confirmed_report,
            expected="boot_is_img_confirmed() called to report current image confirmation state",
            actual="present" if has_confirmed_report else "missing",
            check_type="constraint",
        )
    )

    # Check 6: Version fields all accessed from header struct (not partially read)
    # (LLM failure: only printing major version, ignoring minor/revision)
    version_complete = (
        "major" in generated_code
        and "minor" in generated_code
        and ("revision" in generated_code or "sem_ver" in generated_code)
    )
    details.append(
        CheckDetail(
            check_name="full_version_reported",
            passed=version_complete,
            expected="All version fields (major, minor, revision) reported from header",
            actual="complete" if version_complete else "incomplete version info (missing fields)",
            check_type="constraint",
        )
    )

    # Check 7: print_slot_info (or equivalent) called for both slots via loop or explicit calls
    # (LLM failure: only calling for slot 0 in a function that should check both)
    slot1_info_reported = (
        "slot1_partition" in generated_code
        and "boot_read_bank_header" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="slot1_info_reported",
            passed=slot1_info_reported,
            expected="boot_read_bank_header() called for slot1_partition (secondary slot info reported)",
            actual="present" if slot1_info_reported else "missing (secondary slot never queried)",
            check_type="constraint",
        )
    )

    # Check 8: mcuboot_swap_type() called (swap status is part of slot status query)
    # (LLM failure: reporting slot versions but not the pending swap type)
    has_swap_type_call = "mcuboot_swap_type" in generated_code
    details.append(
        CheckDetail(
            check_name="swap_type_queried",
            passed=has_swap_type_call,
            expected="mcuboot_swap_type() called to include swap status in slot report",
            actual="present" if has_swap_type_call else "missing (swap state not included in status)",
            check_type="constraint",
        )
    )

    return details
