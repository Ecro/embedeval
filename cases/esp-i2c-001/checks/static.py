"""Static checks for ESP-IDF I2C master communication."""
from embedeval.models import CheckDetail


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []

    # Check 1: Must use the new v5.x I2C master header
    has_i2c_master_h = (
        "driver/i2c_master.h" in generated_code
        or "i2c_master.h" in generated_code
    )
    details.append(CheckDetail(
        check_name="i2c_master_header",
        passed=has_i2c_master_h,
        expected="driver/i2c_master.h included (ESP-IDF v5.x API)",
        actual="present" if has_i2c_master_h else "missing",
        check_type="exact_match",
    ))

    # Check 2: app_main entry point
    details.append(CheckDetail(
        check_name="app_main_defined",
        passed="app_main" in generated_code,
        expected="app_main() entry point",
        actual="present" if "app_main" in generated_code else "missing",
        check_type="exact_match",
    ))

    # Check 3: Must use new v5.x I2C master API (not legacy i2c_driver)
    has_new_api = (
        "i2c_master_bus_add_device" in generated_code
        or "i2c_new_master_bus" in generated_code
        or "i2c_master_transmit" in generated_code
    )
    details.append(CheckDetail(
        check_name="i2c_master_new_api",
        passed=has_new_api,
        expected="ESP-IDF v5.x i2c_master_* API used",
        actual="present" if has_new_api else "missing (using deprecated i2c_driver API?)",
        check_type="exact_match",
    ))

    # Check 4: Deprecated legacy driver must NOT be used
    uses_legacy = (
        "i2c_driver_install" in generated_code
        or "i2c_master_write_to_device" in generated_code
    )
    details.append(CheckDetail(
        check_name="no_legacy_i2c_driver",
        passed=not uses_legacy,
        expected="No deprecated i2c_driver_install / i2c_master_write_to_device",
        actual="clean" if not uses_legacy else "found deprecated legacy I2C API",
        check_type="hallucination",
    ))

    # Check 5: No Zephyr APIs
    zephyr_apis = ["i2c_write", "i2c_read", "i2c_write_read", "DEVICE_DT_GET", "k_sleep", "printk"]
    found = [api for api in zephyr_apis if api in generated_code]
    details.append(CheckDetail(
        check_name="no_zephyr_apis",
        passed=not found,
        expected="No Zephyr I2C APIs in ESP-IDF code",
        actual="clean" if not found else f"found Zephyr APIs: {found}",
        check_type="hallucination",
    ))

    return details
