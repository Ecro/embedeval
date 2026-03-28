"""Behavioral checks for Atomic Config Update (Write-then-Commit)."""

import re

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate atomic config update behavioral flow."""
    details: list[CheckDetail] = []

    # Use regex to find actual function call positions (not string literals in printk)
    def find_call_positions(code: str, func_name: str) -> list[int]:
        """Return list of positions where func_name( appears as a real call."""
        return [m.start() for m in re.finditer(r'\b' + re.escape(func_name) + r'\s*\(', code)]

    write_positions = find_call_positions(generated_code, "nvs_write")
    read_positions = find_call_positions(generated_code, "nvs_read")
    delete_positions = find_call_positions(generated_code, "nvs_delete")
    mount_positions = find_call_positions(generated_code, "nvs_mount")

    # Check 1: temp write → verify read → primary write ordering
    # Need at least two nvs_write calls and one nvs_read between them
    temp_write_pos = write_positions[0] if len(write_positions) >= 1 else -1
    primary_write_pos = write_positions[1] if len(write_positions) >= 2 else -1
    read_pos = read_positions[0] if read_positions else -1
    correct_order = (
        temp_write_pos != -1
        and read_pos != -1
        and primary_write_pos != -1
        and temp_write_pos < read_pos < primary_write_pos
    )
    details.append(
        CheckDetail(
            check_name="write_verify_commit_order",
            passed=correct_order,
            expected="nvs_write(temp) → nvs_read(verify) → nvs_write(primary) ordering",
            actual="correct order" if correct_order else "wrong order or in-place update",
            check_type="constraint",
        )
    )

    # Check 2: memcmp verification before primary write
    memcmp_pos = generated_code.find("memcmp")
    verify_before_commit = (
        memcmp_pos != -1
        and primary_write_pos != -1
        and memcmp_pos < primary_write_pos
    )
    details.append(
        CheckDetail(
            check_name="verify_before_commit",
            passed=verify_before_commit,
            expected="memcmp verification occurs before primary slot write",
            actual="correct" if verify_before_commit else "verification missing or after commit",
            check_type="constraint",
        )
    )

    # Check 3: nvs_delete after primary write (cleanup)
    delete_pos = delete_positions[0] if delete_positions else -1
    delete_after_commit = (
        delete_pos != -1
        and primary_write_pos != -1
        and primary_write_pos < delete_pos
    )
    details.append(
        CheckDetail(
            check_name="delete_after_commit",
            passed=delete_after_commit,
            expected="nvs_delete(temp) called after primary commit",
            actual="correct" if delete_after_commit else "delete before commit or missing",
            check_type="constraint",
        )
    )

    # Check 4: CONFIG COMMIT OK printed
    has_commit_ok = "CONFIG COMMIT OK" in generated_code or "COMMIT OK" in generated_code
    details.append(
        CheckDetail(
            check_name="commit_ok_printed",
            passed=has_commit_ok,
            expected="'CONFIG COMMIT OK' printed on successful atomic update",
            actual="present" if has_commit_ok else "missing",
            check_type="constraint",
        )
    )

    # Check 5: Verify mismatch error handled
    has_mismatch_err = (
        "mismatch" in generated_code.lower()
        or ("verify" in generated_code.lower()
            and "failed" in generated_code.lower())
    )
    details.append(
        CheckDetail(
            check_name="verify_mismatch_handled",
            passed=has_mismatch_err,
            expected="Verification mismatch results in error (not silent commit)",
            actual="present" if has_mismatch_err else "missing (may commit corrupt data)",
            check_type="constraint",
        )
    )

    # Check 6: nvs_mount called before any NVS operations at runtime
    # nvs_mount must appear before the first nvs_read/nvs_write call inside main().
    # Helper functions defined before main may contain nvs_write/nvs_read, but they
    # are only executed after main calls them (after nvs_mount).
    main_pos = -1
    for main_pattern in ["int main(", "void main(", "int main(void", "void main(void"]:
        pos = generated_code.find(main_pattern)
        if pos != -1:
            main_pos = pos
            break
    mount_pos = mount_positions[0] if mount_positions else -1
    # Find first nvs_read or nvs_write call inside main() (after main_pos)
    all_nvs_ops = sorted(
        read_positions + write_positions + delete_positions
    )
    first_nvs_op_in_main = next(
        (pos for pos in all_nvs_ops if main_pos != -1 and pos > main_pos), -1
    )
    if first_nvs_op_in_main == -1 and main_pos != -1:
        # nvs ops only in helper functions called from main — check that mount is present
        mount_before_write = mount_pos != -1
    else:
        mount_before_write = (
            mount_pos != -1 and first_nvs_op_in_main != -1 and mount_pos < first_nvs_op_in_main
        )
    details.append(
        CheckDetail(
            check_name="mount_before_nvs_ops",
            passed=mount_before_write,
            expected="nvs_mount() before nvs_write()",
            actual="correct order" if mount_before_write else "wrong order or missing",
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
