"""Static analysis checks for Atomic Config Update (Write-then-Commit)."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate atomic config update code structure."""
    details: list[CheckDetail] = []

    # Check 1: nvs.h included
    has_nvs_h = "zephyr/fs/nvs.h" in generated_code
    details.append(
        CheckDetail(
            check_name="nvs_header_included",
            passed=has_nvs_h,
            expected="zephyr/fs/nvs.h included",
            actual="present" if has_nvs_h else "missing",
            check_type="exact_match",
        )
    )

    # Check 2: Two distinct NVS IDs defined (temp + primary)
    import re
    id_defs = re.findall(r'#define\s+\w*(?:TEMP|PRIM|PRIMARY|BACKUP|STAGING)\w*\s+(\d+)', generated_code)
    # Also count total NVS ID constants defined
    all_ids = re.findall(r'#define\s+\w*(?:ID|NVS_ID|CONFIG_ID)\w*\s+(\d+[Uu]*)', generated_code)
    has_two_ids = len(all_ids) >= 2 or len(id_defs) >= 1
    details.append(
        CheckDetail(
            check_name="two_nvs_ids_defined",
            passed=has_two_ids,
            expected="At least 2 NVS IDs defined (temp/staging + primary)",
            actual=f"found {len(all_ids)} ID constant(s)",
            check_type="constraint",
        )
    )

    # Check 3: nvs_write called at least twice (temp write + primary commit)
    write_calls = len(re.findall(r'\bnvs_write\b', generated_code))
    details.append(
        CheckDetail(
            check_name="two_nvs_writes",
            passed=write_calls >= 2,
            expected="nvs_write() called at least twice (temp + primary)",
            actual=f"found {write_calls} nvs_write call(s)",
            check_type="constraint",
        )
    )

    # Check 4: nvs_read called for verification
    has_read = "nvs_read" in generated_code
    details.append(
        CheckDetail(
            check_name="nvs_read_for_verify",
            passed=has_read,
            expected="nvs_read() called to verify temp write before commit",
            actual="present" if has_read else "missing (no readback verification)",
            check_type="exact_match",
        )
    )

    # Check 5: memcmp used for verification
    has_memcmp = "memcmp" in generated_code
    details.append(
        CheckDetail(
            check_name="memcmp_verification",
            passed=has_memcmp,
            expected="memcmp() used to verify readback matches written data",
            actual="present" if has_memcmp else "missing (no data integrity check)",
            check_type="constraint",
        )
    )

    # Check 6: nvs_delete called to clean temp slot
    has_delete = "nvs_delete" in generated_code
    details.append(
        CheckDetail(
            check_name="temp_slot_deleted",
            passed=has_delete,
            expected="nvs_delete() called to clean up temp slot after commit",
            actual="present" if has_delete else "missing (temp slot not cleaned up)",
            check_type="exact_match",
        )
    )

    return details
