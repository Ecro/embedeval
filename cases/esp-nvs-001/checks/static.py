"""Static checks for ESP-IDF NVS read/write."""
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []

    details.append(CheckDetail(
        check_name="nvs_flash_header",
        passed="nvs_flash.h" in generated_code,
        expected="nvs_flash.h included",
        actual="present" if "nvs_flash.h" in generated_code else "missing",
        check_type="exact_match",
    ))

    details.append(CheckDetail(
        check_name="nvs_header",
        passed="nvs.h" in generated_code,
        expected="nvs.h included",
        actual="present" if "nvs.h" in generated_code else "missing",
        check_type="exact_match",
    ))

    details.append(CheckDetail(
        check_name="app_main_defined",
        passed="app_main" in generated_code,
        expected="app_main() entry point",
        actual="present" if "app_main" in generated_code else "missing",
        check_type="exact_match",
    ))

    details.append(CheckDetail(
        check_name="nvs_flash_init_called",
        passed="nvs_flash_init" in generated_code,
        expected="nvs_flash_init() called before nvs_open",
        actual="present" if "nvs_flash_init" in generated_code else "missing",
        check_type="exact_match",
    ))

    details.append(CheckDetail(
        check_name="nvs_open_called",
        passed="nvs_open" in generated_code,
        expected="nvs_open() called",
        actual="present" if "nvs_open" in generated_code else "missing",
        check_type="exact_match",
    ))

    details.append(CheckDetail(
        check_name="nvs_set_i32_called",
        passed="nvs_set_i32" in generated_code,
        expected="nvs_set_i32() called to write value",
        actual="present" if "nvs_set_i32" in generated_code else "missing",
        check_type="exact_match",
    ))

    details.append(CheckDetail(
        check_name="nvs_commit_called",
        passed="nvs_commit" in generated_code,
        expected="nvs_commit() called before close",
        actual="present" if "nvs_commit" in generated_code else "missing",
        check_type="exact_match",
    ))

    details.append(CheckDetail(
        check_name="nvs_close_called",
        passed="nvs_close" in generated_code,
        expected="nvs_close() called to release handle",
        actual="present" if "nvs_close" in generated_code else "missing",
        check_type="exact_match",
    ))

    # Cross-platform hallucination checks
    zephyr_apis = ["settings_load", "settings_save", "k_sleep", "DEVICE_DT_GET"]
    found_zephyr = [api for api in zephyr_apis if api in generated_code]
    details.append(CheckDetail(
        check_name="no_zephyr_apis",
        passed=not found_zephyr,
        expected="No Zephyr settings/storage APIs",
        actual="clean" if not found_zephyr else f"found Zephyr APIs: {found_zephyr}",
        check_type="hallucination",
    ))

    posix_apis = ["fopen", "fwrite", "fread", "fclose"]
    found_posix = [api for api in posix_apis if api in generated_code]
    details.append(CheckDetail(
        check_name="no_posix_file_apis",
        passed=not found_posix,
        expected="No POSIX file I/O (use NVS, not fopen/fwrite)",
        actual="clean" if not found_posix else f"found POSIX file APIs: {found_posix}",
        check_type="hallucination",
    ))

    return details
