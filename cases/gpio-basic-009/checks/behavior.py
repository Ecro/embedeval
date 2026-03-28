"""Behavioral checks for multi-UART runtime baudrate change application."""

from embedeval.models import CheckDetail
from embedeval.check_utils import check_no_cross_platform_apis


def run_checks(generated_code: str) -> list[CheckDetail]:
    """Validate multi-UART behavioral properties and domain invariants."""
    details: list[CheckDetail] = []

    # Check 1: device_is_ready called for both UARTs
    ready_count = generated_code.count("device_is_ready")
    both_checked = ready_count >= 2
    details.append(
        CheckDetail(
            check_name="both_uarts_ready_checked",
            passed=both_checked,
            expected="device_is_ready() called for both UARTs (>=2 times)",
            actual=f"device_is_ready called {ready_count} time(s)",
            check_type="constraint",
        )
    )

    # Check 2: uart_configure called at least twice (initial config + runtime change)
    configure_count = generated_code.count("uart_configure")
    reconfigured = configure_count >= 2
    details.append(
        CheckDetail(
            check_name="uart_reconfigured_at_runtime",
            passed=reconfigured,
            expected="uart_configure() called at least twice (runtime baudrate change)",
            actual=f"uart_configure called {configure_count} time(s)",
            check_type="constraint",
        )
    )

    # Check 3: Error handling for uart_configure return values
    has_error_check = "< 0" in generated_code or "!= 0" in generated_code
    details.append(
        CheckDetail(
            check_name="uart_configure_error_checked",
            passed=has_error_check,
            expected="Return value of uart_configure() checked for error",
            actual="present" if has_error_check else "missing",
            check_type="constraint",
        )
    )

    # Check 4: Different baudrates configured (115200 and 9600 or similar)
    import re
    baudrates = set(re.findall(r"baudrate\s*=\s*(\d+)", generated_code))
    multiple_baudrates = len(baudrates) >= 2
    details.append(
        CheckDetail(
            check_name="multiple_baudrates_configured",
            passed=multiple_baudrates,
            expected="At least 2 different baudrates configured",
            actual=f"baudrates found: {baudrates}",
            check_type="constraint",
        )
    )

    # Check 5: Cross-platform — no FreeRTOS APIs
    has_freertos = any(
        p in generated_code for p in ["xQueueSend", "vTaskDelay", "xTaskCreate"]
    )
    details.append(
        CheckDetail(
            check_name="no_freertos_apis",
            passed=not has_freertos,
            expected="No FreeRTOS APIs (wrong RTOS)",
            actual="FreeRTOS API found" if has_freertos else "clean",
            check_type="constraint",
        )
    )

    # Check 6: Ends with k_sleep(K_FOREVER)
    has_forever = "K_FOREVER" in generated_code
    details.append(
        CheckDetail(
            check_name="sleeps_forever",
            passed=has_forever,
            expected="k_sleep(K_FOREVER) used at end of main",
            actual="present" if has_forever else "missing",
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
