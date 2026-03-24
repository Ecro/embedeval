"""Behavioral checks for BLE bond management."""

from embedeval.check_utils import check_no_cross_platform_apis
from embedeval.models import CheckDetail

_BLE_HALLUCINATED_APIS = [
    "BLEDevice.connect",
    "BLEDevice.init",
    "gap_connect(",
    "ble_gap_connect(",
    "esp_ble_gap_",
    "esp_bt_",
    "nimble_port_",
]


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate BLE bond management ordering and correctness."""
    details: list[CheckDetail] = []

    # Check 1: No cross-platform BLE API hallucinations
    cross_platform_hits = check_no_cross_platform_apis(
        generated_code, skip_platforms=["POSIX", "Linux_Userspace"]
    )
    ble_hallucinations = [
        api for api in _BLE_HALLUCINATED_APIS if api in generated_code
    ]
    no_wrong_apis = not cross_platform_hits and not ble_hallucinations
    details.append(
        CheckDetail(
            check_name="no_cross_platform_ble_apis",
            passed=no_wrong_apis,
            expected="Only Zephyr BLE APIs; no Arduino/NimBLE/ESP-IDF APIs",
            actual=(
                "clean"
                if no_wrong_apis
                else f"found: {[x[0] for x in cross_platform_hits] + ble_hallucinations}"
            ),
            check_type="hallucination",
        )
    )

    # Check 2: bt_enable BEFORE settings_load and bond operations
    enable_pos = generated_code.find("bt_enable")
    settings_pos = generated_code.find("settings_load")
    foreach_pos = generated_code.find("bt_foreach_bond")

    enable_before_settings = (
        enable_pos != -1
        and (settings_pos == -1 or enable_pos < settings_pos)
    )
    enable_before_foreach = (
        enable_pos != -1
        and (foreach_pos == -1 or enable_pos < foreach_pos)
    )
    details.append(
        CheckDetail(
            check_name="bt_enable_before_bond_ops",
            passed=enable_before_settings and enable_before_foreach,
            expected="bt_enable() called before settings_load() and bt_foreach_bond()",
            actual="correct" if (enable_before_settings and enable_before_foreach)
                   else "wrong order — bond operations require bt_enable first",
            check_type="constraint",
        )
    )

    # Check 3: settings_load BEFORE bt_foreach_bond
    settings_before_foreach = (
        settings_pos != -1
        and foreach_pos != -1
        and settings_pos < foreach_pos
    )
    details.append(
        CheckDetail(
            check_name="settings_load_before_foreach_bond",
            passed=settings_before_foreach,
            expected="settings_load() before bt_foreach_bond() to include persisted bonds",
            actual="correct" if settings_before_foreach else "wrong order — bonds not yet loaded",
            check_type="constraint",
        )
    )

    # Check 4: Bond callback uses BT_ID_DEFAULT
    has_default_id = "BT_ID_DEFAULT" in generated_code
    details.append(
        CheckDetail(
            check_name="bt_id_default_used",
            passed=has_default_id,
            expected="BT_ID_DEFAULT used for bond operations",
            actual="present" if has_default_id else "missing — identity not specified",
            check_type="exact_match",
        )
    )

    # Check 5: Bond callback increments or counts bonds
    has_count = (
        "count" in generated_code
        and ("bond_count" in generated_code or "(*count)" in generated_code)
    )
    details.append(
        CheckDetail(
            check_name="bond_count_tracked",
            passed=has_count,
            expected="Bond count tracked in bt_foreach_bond callback",
            actual="present" if has_count else "missing — no bond count output",
            check_type="constraint",
        )
    )

    # Check 6: bt_unpair uses NULL addr to remove all bonds (not just one)
    has_unpair_null = "bt_unpair(BT_ID_DEFAULT, NULL)" in generated_code
    details.append(
        CheckDetail(
            check_name="bt_unpair_removes_all",
            passed=has_unpair_null,
            expected="bt_unpair(BT_ID_DEFAULT, NULL) removes all bonds",
            actual="present" if has_unpair_null else "missing — specific address required for remove-all",
            check_type="exact_match",
        )
    )

    # Check 7: bt_enable error checked
    enable_idx = generated_code.find("bt_enable")
    post_enable = generated_code[enable_idx:enable_idx + 100] if enable_idx != -1 else ""
    has_enable_check = enable_idx != -1 and (
        "if (err" in post_enable or "if (ret" in post_enable
    )
    details.append(
        CheckDetail(
            check_name="bt_enable_error_checked",
            passed=has_enable_check,
            expected="bt_enable() return value checked for error",
            actual="present" if has_enable_check else "missing",
            check_type="constraint",
        )
    )

    # Check 8: settings_load error checked
    # LLM failure: calls settings_load without checking return value
    settings_idx = generated_code.find("settings_load")
    post_settings = generated_code[settings_idx:settings_idx + 100] if settings_idx != -1 else ""
    has_settings_check = settings_idx != -1 and (
        "if (err" in post_settings or "if (ret" in post_settings or "< 0" in post_settings
    )
    details.append(
        CheckDetail(
            check_name="settings_load_error_checked",
            passed=has_settings_check,
            expected="settings_load() return value checked for error",
            actual="present" if has_settings_check else "missing",
            check_type="constraint",
        )
    )

    return details
