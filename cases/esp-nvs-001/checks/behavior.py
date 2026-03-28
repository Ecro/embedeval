"""Behavioral checks for ESP-IDF NVS read/write."""
from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []

    # Check 1: NVS flash init handles page/version errors
    has_nvs_recovery = (
        "ESP_ERR_NVS_NO_FREE_PAGES" in generated_code
        or "ESP_ERR_NVS_NEW_VERSION_FOUND" in generated_code
    )
    details.append(CheckDetail(
        check_name="nvs_flash_init_error_recovery",
        passed=has_nvs_recovery,
        expected="Handle ESP_ERR_NVS_NO_FREE_PAGES / ESP_ERR_NVS_NEW_VERSION_FOUND",
        actual="present" if has_nvs_recovery else "missing (required for production use)",
        check_type="constraint",
    ))

    # Check 2: nvs_flash_init called before nvs_open
    flash_init_pos = generated_code.find("nvs_flash_init")
    open_pos = generated_code.find("nvs_open")
    flash_before_open = (
        flash_init_pos != -1 and (open_pos == -1 or flash_init_pos < open_pos)
    )
    details.append(CheckDetail(
        check_name="flash_init_before_open",
        passed=flash_before_open,
        expected="nvs_flash_init() called before nvs_open()",
        actual="correct order" if flash_before_open else "wrong order or missing",
        check_type="constraint",
    ))

    # Check 3: ESP_ERR_NVS_NOT_FOUND handled for missing key
    has_not_found_handling = "ESP_ERR_NVS_NOT_FOUND" in generated_code
    details.append(CheckDetail(
        check_name="not_found_key_handled",
        passed=has_not_found_handling,
        expected="ESP_ERR_NVS_NOT_FOUND handled (key may not exist on first run)",
        actual="present" if has_not_found_handling else "missing (unhandled on first boot)",
        check_type="constraint",
    ))

    # Check 4: nvs_commit called before the final nvs_close
    # Use rfind to get the last occurrence (error paths may close early)
    commit_pos = generated_code.rfind("nvs_commit")
    close_pos = generated_code.rfind("nvs_close")
    commit_before_close = (
        commit_pos != -1 and (close_pos == -1 or commit_pos < close_pos)
    )
    details.append(CheckDetail(
        check_name="commit_before_close",
        passed=commit_before_close,
        expected="nvs_commit() called before nvs_close() to persist data",
        actual="correct order" if commit_before_close else "wrong order or missing commit",
        check_type="constraint",
    ))

    # Check 5: nvs_get_i32 return value checked
    get_pos = generated_code.find("nvs_get_i32")
    post_get = generated_code[get_pos:get_pos + 300] if get_pos != -1 else ""
    has_get_check = "ESP_OK" in post_get or "!= ESP_OK" in post_get or "ret" in post_get
    details.append(CheckDetail(
        check_name="nvs_get_error_checked",
        passed=has_get_check,
        expected="nvs_get_i32() return value checked",
        actual="present" if has_get_check else "missing",
        check_type="constraint",
    ))

    # Check 6: nvs_set_i32 return value checked
    set_pos = generated_code.find("nvs_set_i32")
    post_set = generated_code[set_pos:set_pos + 300] if set_pos != -1 else ""
    has_set_check = "ESP_OK" in post_set or "!= ESP_OK" in post_set or "ret" in post_set
    details.append(CheckDetail(
        check_name="nvs_set_error_checked",
        passed=has_set_check,
        expected="nvs_set_i32() return value checked",
        actual="present" if has_set_check else "missing",
        check_type="constraint",
    ))

    # Check 7: No POSIX file operations
    posix_apis = ["fopen", "fwrite", "fread", "fprintf"]
    found_posix = [api for api in posix_apis if api in generated_code]
    details.append(CheckDetail(
        check_name="no_posix_file_ops",
        passed=not found_posix,
        expected="No POSIX file I/O (use NVS API, not file system)",
        actual="clean" if not found_posix else f"found: {found_posix}",
        check_type="hallucination",
    ))

    # Check: No cross-platform API contamination
    cross_plat = check_no_cross_platform_apis(generated_code, skip_platforms=["Linux_Userspace", "FreeRTOS"])
    details.append(CheckDetail(
        check_name="no_cross_platform_apis",
        passed=len(cross_plat) == 0,
        expected="No Arduino/STM32_HAL/POSIX APIs",
        actual="clean" if not cross_plat else f"found: {[a for a, _ in cross_plat]}",
        check_type="constraint",
    ))

    return details
