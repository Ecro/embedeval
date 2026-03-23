"""Behavioral checks for BLE central (scanner + connect)."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate BLE central scan-connect-discover ordering and ref management."""
    details: list[CheckDetail] = []

    # Check 1: scan before connect (ordering)
    # bt_le_scan_start must be called (in main) and bt_conn_le_create must appear somewhere.
    # The scan callback (scan_recv) calls bt_conn_le_create after scanning found a device,
    # so we only require both are present — the scan must start before any connection can occur.
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

    # Check 2: bt_conn_unref called in disconnected callback (ref management)
    # Find the disconnected callback function body and check for bt_conn_unref inside it.
    import re
    disconnected_fn_match = re.search(
        r"(?:void\s+disconnected|\.disconnected\s*=)\s*[^{]*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}",
        generated_code,
        re.DOTALL,
    )
    if disconnected_fn_match:
        disconnected_body = disconnected_fn_match.group(1)
        unref_in_disconnected = "bt_conn_unref" in disconnected_body
    else:
        # Fall back: unref must appear after disconnected definition
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

    # Check 3: GATT discovery after connected (ordering)
    # bt_gatt_discover must be called inside the connected callback.
    # Use position: bt_gatt_discover must appear after "void connected" definition.
    connected_pos = generated_code.find("void connected")
    if connected_pos == -1:
        connected_pos = generated_code.find(".connected")
    gatt_pos = re.search(r"\bbt_gatt_discover\s*\(", generated_code)
    gatt_pos = gatt_pos.start() if gatt_pos else -1
    # bt_gatt_discover must appear after the connected callback definition starts
    discover_after_connected = connected_pos != -1 and gatt_pos != -1 and gatt_pos > connected_pos
    details.append(
        CheckDetail(
            check_name="discovery_after_connected",
            passed=discover_after_connected,
            expected="bt_gatt_discover() called inside connected callback",
            actual="correct" if discover_after_connected else "wrong — discovery before connection established",
            check_type="constraint",
        )
    )

    # Check 4: scan stopped before connecting (stop scan then connect)
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

    # Check 5: default_conn set to NULL after disconnect
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

    return details
