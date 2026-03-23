"""Behavioral checks for BLE GATT custom service."""

from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate BLE GATT behavioral properties."""
    details: list[CheckDetail] = []

    # Check 1: bt_enable before bt_le_adv_start
    enable_pos = generated_code.find("bt_enable")
    adv_pos = generated_code.find("bt_le_adv_start")
    order_ok = enable_pos != -1 and adv_pos != -1 and enable_pos < adv_pos
    details.append(
        CheckDetail(
            check_name="enable_before_advertise",
            passed=order_ok,
            expected="bt_enable() before bt_le_adv_start()",
            actual="correct" if order_ok else "wrong order",
            check_type="constraint",
        )
    )

    # Check 2: Custom 128-bit UUID defined (not standard 16-bit)
    has_128bit = (
        "BT_UUID_128_ENCODE" in generated_code
        or "BT_UUID_INIT_128" in generated_code
        or "BT_UUID_DECLARE_128" in generated_code
    )
    details.append(
        CheckDetail(
            check_name="custom_128bit_uuid",
            passed=has_128bit,
            expected="128-bit custom UUID defined",
            actual="present" if has_128bit else "missing (using 16-bit?)",
            check_type="exact_match",
        )
    )

    # Check 3: Characteristic has both READ and WRITE
    has_read = "BT_GATT_CHRC_READ" in generated_code
    has_write = "BT_GATT_CHRC_WRITE" in generated_code
    details.append(
        CheckDetail(
            check_name="read_write_characteristic",
            passed=has_read and has_write,
            expected="Characteristic with READ and WRITE properties",
            actual=f"read={has_read}, write={has_write}",
            check_type="constraint",
        )
    )

    # Check 4: Read callback uses bt_gatt_attr_read
    # (LLM failure: raw memcpy without bounds check)
    has_attr_read = "bt_gatt_attr_read" in generated_code
    details.append(
        CheckDetail(
            check_name="read_uses_attr_read",
            passed=has_attr_read,
            expected="Read callback uses bt_gatt_attr_read()",
            actual="present" if has_attr_read else "missing",
            check_type="exact_match",
        )
    )

    # Check 5: Error handling for bt_enable
    has_err_check = (
        "err" in generated_code or "ret" in generated_code
    ) and ("if" in generated_code)
    details.append(
        CheckDetail(
            check_name="bt_enable_error_check",
            passed=has_err_check,
            expected="Error check on bt_enable() return",
            actual="present" if has_err_check else "missing",
            check_type="constraint",
        )
    )

    # Check 6: BT_GATT_PRIMARY_SERVICE in service definition
    has_primary = "BT_GATT_PRIMARY_SERVICE" in generated_code
    details.append(
        CheckDetail(
            check_name="primary_service_attribute",
            passed=has_primary,
            expected="BT_GATT_PRIMARY_SERVICE in service definition",
            actual="present" if has_primary else "missing",
            check_type="exact_match",
        )
    )

    return details
