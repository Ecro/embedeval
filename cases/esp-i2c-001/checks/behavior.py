"""Behavioral checks for ESP-IDF I2C master communication."""
from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    details: list[CheckDetail] = []

    # Check 1: Error handling on bus/device init
    has_error_check = (
        "ESP_OK" in generated_code
        and ("!= ESP_OK" in generated_code or "ESP_ERROR_CHECK" in generated_code)
    )
    details.append(CheckDetail(
        check_name="error_handling_present",
        passed=has_error_check,
        expected="I2C API return values checked (ESP_OK / ESP_ERROR_CHECK)",
        actual="present" if has_error_check else "missing",
        check_type="constraint",
    ))

    # Check 2: Bus cleanup — device removed before bus deleted
    has_dev_cleanup = (
        "i2c_master_bus_rm_device" in generated_code
        or "i2c_del_master_bus" in generated_code
    )
    details.append(CheckDetail(
        check_name="i2c_bus_cleanup",
        passed=has_dev_cleanup,
        expected="I2C bus/device cleaned up (i2c_master_bus_rm_device or i2c_del_master_bus)",
        actual="present" if has_dev_cleanup else "missing (resource leak)",
        check_type="constraint",
    ))

    # Check 3: transmit_receive used for combined write-then-read
    has_tx_rx = "i2c_master_transmit_receive" in generated_code
    details.append(CheckDetail(
        check_name="transmit_receive_used",
        passed=has_tx_rx,
        expected="i2c_master_transmit_receive() for combined write-then-read",
        actual="present" if has_tx_rx else "missing (separate transmit/receive calls are also acceptable)",
        check_type="constraint",
    ))

    # Check 4: No Arduino Wire library
    arduino_wire_apis = ["Wire.begin", "Wire.write", "Wire.read", "Wire.requestFrom"]
    found_arduino = [api for api in arduino_wire_apis if api in generated_code]
    details.append(CheckDetail(
        check_name="no_arduino_wire",
        passed=not found_arduino,
        expected="No Arduino Wire library APIs",
        actual="clean" if not found_arduino else f"found Arduino Wire: {found_arduino}",
        check_type="hallucination",
    ))

    # Check 5: Sensor address 0x68 referenced
    has_sensor_addr = "0x68" in generated_code
    details.append(CheckDetail(
        check_name="sensor_address_0x68",
        passed=has_sensor_addr,
        expected="Sensor I2C address 0x68 used",
        actual="present" if has_sensor_addr else "missing",
        check_type="constraint",
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
