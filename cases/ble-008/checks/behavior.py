"""Behavioral checks for BLE central (scanner + connect)."""

import re

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
    """Validate BLE central scan-connect-discover ordering and ref management."""
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

    # Check 2: bt_enable before bt_le_scan_start (ordering)
    enable_pos = generated_code.find("bt_enable")
    scan_pos = generated_code.find("bt_le_scan_start")
    enable_before_scan = enable_pos != -1 and scan_pos != -1 and enable_pos < scan_pos
    details.append(
        CheckDetail(
            check_name="bt_enable_before_scan",
            passed=enable_before_scan,
            expected="bt_enable() before bt_le_scan_start()",
            actual="correct" if enable_before_scan else "wrong order",
            check_type="constraint",
        )
    )

    # Check 3: scan before connect (both must be present)
    has_scan_start = "bt_le_scan_start" in generated_code
    has_conn_create = "bt_conn_le_create" in generated_code
    scan_before_connect = has_scan_start and has_conn_create
    details.append(
        CheckDetail(
            check_name="scan_before_connect",
            passed=scan_before_connect,
            expected="bt_le_scan_start() present (scanning initiated before connecting)",
            actual="correct" if scan_before_connect else "wrong order — must scan to find device first",
            check_type="constraint",
        )
    )

    # Check 4: bt_conn_unref called in disconnected callback (ref management)
    disconnected_fn_match = re.search(
        r"(?:void\s+disconnected|\.disconnected\s*=)\s*[^{]*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}",
        generated_code,
        re.DOTALL,
    )
    if disconnected_fn_match:
        disconnected_body = disconnected_fn_match.group(1)
        unref_in_disconnected = "bt_conn_unref" in disconnected_body
    else:
        disconnected_pos = generated_code.find("void disconnected")
        if disconnected_pos == -1:
            disconnected_pos = generated_code.find(".disconnected")
        unref_pos = generated_code.find("bt_conn_unref", disconnected_pos) if disconnected_pos != -1 else -1
        unref_in_disconnected = disconnected_pos != -1 and unref_pos != -1
    details.append(
        CheckDetail(
            check_name="conn_unref_in_disconnected",
            passed=unref_in_disconnected,
            expected="bt_conn_unref() called in disconnected callback",
            actual="present" if unref_in_disconnected else "missing — connection ref leaked",
            check_type="constraint",
        )
    )

    # Check 5: GATT discovery after connected (ordering)
    connected_pos = generated_code.find("void connected")
    if connected_pos == -1:
        connected_pos = generated_code.find(".connected")
    gatt_pos = re.search(r"\bbt_gatt_discover\s*\(", generated_code)
    gatt_pos_int = gatt_pos.start() if gatt_pos else -1
    discover_after_connected = connected_pos != -1 and gatt_pos_int != -1 and gatt_pos_int > connected_pos
    details.append(
        CheckDetail(
            check_name="discovery_after_connected",
            passed=discover_after_connected,
            expected="bt_gatt_discover() called inside connected callback",
            actual="correct" if discover_after_connected else "wrong — discovery before connection established",
            check_type="constraint",
        )
    )

    # Check 6: scan stopped before connecting (stop scan then connect)
    scan_stop_pos = generated_code.find("bt_le_scan_stop")
    create_pos = generated_code.find("bt_conn_le_create")
    stop_before_create = (
        scan_stop_pos != -1 and create_pos != -1 and scan_stop_pos < create_pos
    )
    details.append(
        CheckDetail(
            check_name="scan_stopped_before_connect",
            passed=stop_before_create,
            expected="bt_le_scan_stop() called before bt_conn_le_create()",
            actual="correct" if stop_before_create else "scanning while connecting causes conflicts",
            check_type="constraint",
        )
    )

    # Check 7: default_conn set to NULL after disconnect
    has_null_assign = "default_conn = NULL" in generated_code or "= NULL" in generated_code
    details.append(
        CheckDetail(
            check_name="default_conn_cleared_on_disconnect",
            passed=has_null_assign,
            expected="default_conn set to NULL after disconnection",
            actual="present" if has_null_assign else "missing — stale pointer after disconnect",
            check_type="constraint",
        )
    )

    # Check 8: bt_enable error checked
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

    # Check 9: conn_cleanup_on_failed_connect (error path cleanup in connected callback)
    # LLMs often handle the happy path but forget bt_conn_unref + NULL assignment when err != 0.
    connected_cb_pos = generated_code.find("void connected")
    if connected_cb_pos == -1:
        # Resolve function name from struct assignment: .connected = fn_name
        cb_name_match = re.search(r"\.connected\s*=\s*(\w+)", generated_code)
        if cb_name_match:
            fn_name = cb_name_match.group(1)
            connected_cb_pos = generated_code.find(f"void {fn_name}")
    conn_cleanup_ok = False
    if connected_cb_pos != -1:
        # Locate the error check block within the connected callback body
        cb_slice = generated_code[connected_cb_pos:connected_cb_pos + 600]
        err_block_match = re.search(r"if\s*\(\s*err", cb_slice)
        if err_block_match:
            err_block_start = err_block_match.start()
            err_block_text = cb_slice[err_block_start:err_block_start + 400]
            conn_cleanup_ok = (
                "bt_conn_unref" in err_block_text
                and "= NULL" in err_block_text
            )
    details.append(
        CheckDetail(
            check_name="conn_cleanup_on_failed_connect",
            passed=conn_cleanup_ok,
            expected=(
                "In connected callback error block: bt_conn_unref() called "
                "and connection pointer set to NULL"
            ),
            actual=(
                "present" if conn_cleanup_ok
                else "missing — connection ref leaked on failed connect"
            ),
            check_type="constraint",
        )
    )

    return details
